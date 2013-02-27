from webapp import redisdb as db
from webapp.models import LcUser
from webapp.models import Thread, Comment
from django.db import connection
import traceback
from time import time
import redis

# Remove threads older than DENGO_TIME_LIMIT seconds
DENGO_TIME_LIMIT = 2*24*60*60
LCDB = 1

def arxiv_threads(tids):
    """
        Put threads with ids [tids] to archive
        Tags and comments of the thread are also stored
    """
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
                    print "Thread is not in DB."
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
                            tag.save()
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
                    #
                    # ... MISSING ...
                    print "Thread saved"
                else:
                    print "Thread is in DB"
                    #
                    # Remove thread data from redis
                    #
                    # ... MISSING ...
            else:
                print "Thread is new"
        return (True,tids) # threads are in archive
    except:
        connection._rollback()
        return (False,str(traceback.format_exc()))
        
