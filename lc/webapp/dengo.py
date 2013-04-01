from webapp import redisdb as db
from webapp.models import LcUser
from webapp.models import Thread, Comment
from django.db import connection
import traceback
from time import time
import redis
import msgpack

# Remove threads older than DENGO_TIME_LIMIT seconds
DENGO_TIME_LIMIT = 2*24*60*60
# Dengo arxiv old threads in every DENGO_ARXIV seconds
DENGO_ARXIV_INTERVAL = 12*60*60
LCDB = 1

def arxiv():
    r = redis.Redis(db = LCDB)
    # Check the timestamp
    if not r.exists('dengo'):
        r.set('dengo',int(time()))
        r.expire('dengo',DENGO_ARXIV_INTERVAL)
        tids = r.lrange('act:ids',0, -1)
        begin = time()
        arxiv_threads(tids,r)
        elapsed = time() - begin
        print "Elapsed time: "+str(elapsed)

def arxiv_threads(tids,r):
    """
        Put threads with ids [tids] to archive
        Tags and comments of the thread are also stored
    """
    deleted_comments = []
    deleted_threads = []
    try:
        headers = db.get_thread_headers(tids)
        for h in headers:
            if (int(time()) - int(h['time']))>DENGO_TIME_LIMIT:
                creator = LcUser.objects.get(pk = h['cid'])
                try:
                    Thread.objects.get(id=h['id'])
                except Thread.DoesNotExist:
                    #
                    # Save the thread
                    #
                    t = Thread(id=h['id'],
                               creator=creator,
                               title=h['title'],
                               summary=h['summary'],
                               suggested_title=h['suggested_title'],
                               url = h['url'],
                               domain = h['domain'],
                               time_created = h['time'])
                    t.save()
                    #
                    # Save tags
                    #
                    for redistag in h['tags']:
                        tagid = redistag[0]
                        tagname = redistag[1]
                        tag = Tag.objects.filter(name = tagname)
                        if len(tag) == 0:
                            tag = Tag(id = tagid, name = tagname)
                            tag.threads.add(t)
                            tag.save()
                        else:
                            tag = tag[0]
                            if len(tag.threads.filter(id = t.id)) == 0:
                                tag.threads.add(t)
                                tag.save()
                    #
                    # Save comments
                    #
                    cids = db.get_thread_comments(h['id'])
                    comments = db.get_comments(cids)
                    for comment in comments:
                        if comment['pid'] != -1:
                            try:
                                parent = Comment.objects.get(pk = comment['pid'])
                            except:
                                connection._rollback()
                                parent = None
                        else:
                            parent = None
                        c = Comment(id = comment['cid'],
                                    creator=creator,
                                    thread = t,
                                    parent = parent,
                                    text=comment['text'],
                                    time_created = comment['time'],
                                    up = comment['up'],
                                    down = comment['down'])
                        c.save()
                    #
                    # Remove thread data from redis
                    # Later: Put into a function
                    #
                    # Remove thread header
                    r.delete('t:'+str(h['id']))
                    # Remove thread from active thread id list
                    r.lrem('act:ids',h['id'])
                    # Remove thread ids from t:tags:<tid>
                    tagids = r.lrange('t:tags:'+str(h['id']),0,-1)
                    r.delete('t:tags:'+str(h['id']))
                    for tagid in tagids:
                        r.zrem('tag:t:'+str(tagid),h['id'])
                    # Remove comments associated with tid
                    cids = r.lrange('t:comm:'+str(h['id']),0,-1)
                    deleted_comments = deleted_comments + cids
                    r.delete('t:comm:'+str(h['id']))
                    for cid in cids:
                        r.delete('c:'+str(cid))
                        r.delete('c:up:'+str(cid))
                        r.delete('c:down:'+str(cid))
                    # Remove follower data
                    foll_uids = r.smembers('t:foll:'+str(h['id']))
                    for uid in foll_uids:
                        r.srem('u:foll:'+str(uid),str(h['id']))
                    r.delete('t:foll:'+str(h['id']))
                    deleted_threads = deleted_threads + [h['id']]
                else:
                    #
                    # Remove thread data from redis
                    # Later: Put into a function
                    #
                    # Remove thread header
                    r.delete('t:'+str(h['id']))
                    # Remove thread from active thread id list
                    r.lrem('act:ids',h['id'])
                    # Remove thread ids from t:tags:<tid>
                    tagids = r.lrange('t:tags:'+str(h['id']),0,-1)
                    r.delete('t:tags:'+str(h['id']))
                    for tagid in tagids:
                        r.zrem('tag:t:'+str(tagid),h['id'])
                    # Remove comments associated with tid
                    cids = r.lrange('t:comm:'+str(h['id']),0,-1)
                    deleted_comments = deleted_comments + cids
                    r.delete('t:comm:'+str(h['id']))
                    for cid in cids:
                        r.delete('c:'+str(cid))
                        r.delete('c:up:'+str(cid))
                        r.delete('c:down:'+str(cid))
                    # Remove follower data
                    foll_uids = r.smembers('t:foll:'+str(h['id']))
                    for uid in foll_uids:
                        r.srem('u:foll:'+str(uid),str(h['id']))
                    r.delete('t:foll:'+str(h['id']))
                    deleted_threads = deleted_threads + [h['id']]
            else:
                print "Thread is new"
        # Delete the sorted act:id list since if act:id has been updated
        if not deleted_threads:
            r.delete('act:ids:sorted')
        # Update user keys - remove archived comments from u:up u:down u:comm
        for comment_id in deleted_comments:
            u_up_keys = r.keys('u:up:*')
            for key in u_up_keys:
                r.srem(key,str(comment_id))
            u_down_keys = r.keys('u:down:*')
            for key in u_down_keys:
                r.srem(key,str(comment_id))
            u_comm_keys = r.keys('u:comm:*')
            for key in u_comm_keys:
                r.lrem(key,comment_id)
        # Update user keys - remove archived threads from u:notif
        u_notif_keys = r.keys('u:notif:*')
        for key in u_notif_keys:
            for i,notif in enumerate(r.zrange(key,0,-1)):
                notif_data = msgpack.unpackb(notif)
                if notif_data['tid'] in deleted_threads:
                    # NOTE: works only for redis 2.0+
                    r.zremrangebyrank(key,i,i)
        # Remove empty tag keys
        tag_threads = r.keys('tag:t:*')
        for t in tag_threads:
            if len(r.zrange(t,0,-1))==0:
                tagid = int(t.split(':')[2])
                tagname = r.get('tag:'+str(tagid))
                r.delete('tag:'+str(tagid))
                r.delete('tag:'+str(tagname))
        return (True,deleted_threads) # threads are in archive
    except:
        connection._rollback()
        return (False,str(traceback.format_exc()))
        
