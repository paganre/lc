import redis
import msgpack
import os
from time import time

"""
Redis Structures:
-----------------
 Thread-Lists:
  .act:ids          list of active ids in a time-sorted manner
  act:sorted:ids   list of active ids in an algorithm-sorted manner
 Threads:
  .t:<tid>          msgpacked thread-header of thread (see: aux-structures)
  .t:tags:<tid>     list of tag-ids for thread
  .t:comm:<tid>     list of comment-ids for thread in a time-sorted manner
  ..t:foll:<tid>     set of followers of the thread
 Tags:
  .tag:<tagid>      name of the tag
  .tag:<tagname>    id of the tag
  .tag:t:<tagid>    thread list of the tags in a time-sorted manner
 Comments:
  .c:<cid>          msgpacked comment (see:aux-structures)
  ..c:up:<cid>       up-votes of comment
  ..c:down:<cid>     down-votes of comment
 Users:
  .u:<uid>          username of user
  .u:<uname>        id of user
  .u:comm:<uid>     comment-list of user
  ..u:up:<uid>       user's up-voted comment set
  ..u:down:<uid>     user's down-voted comment set
  .u:time:<uid>     user's time of join
  ..u:foll:<uid>     set of thread-id's that user is following
  u:notif:<uid>    sorted-set of notifications for user with score = timestamp (see: aux-structures)  

Aux Structures:
---------------
 thread-header: {title,summary,url,domain,time,cid,cname,up,down,views}
 comment: {text,time,pid,cid,cname} [pid is parent id it's either -1 or a comment id]
 notification: {tid,cid,type} [type is either 1 (reply) or 0 (follow-notif)]

"""


THREAD_PER_PAGE = 10
LCDB = 1


# tested
def get_thread_ids(page = 0, algorithm = False):
    """
    thread id pagination, if algo = False returns time-sorted
    """
    r = redis.Redis(db=LCDB)
    if algorithm:
        return [int(tid) for tid in r.lrange('act:sorted:ids',page*THREAD_PER_PAGE, (page+1)*THREAD_PER_PAGE -1)]
    return [int(tid) for tid in r.lrange('act:ids',page*THREAD_PER_PAGE, (page+1)*THREAD_PER_PAGE-1)]


# tested
def get_all_threads():
    r = redis.Redis(db=LCDB)
    return [int(tid) for tid in r.lrange('act:ids',0,-1)]


# tested
def get_user_comments(uid):
    r = redis.Redis(db=LCDB)
    return [int(cid) for cid in r.lrange('u:comm:'+str(uid),0,-1)]


# tested
def get_user_follows(uid):
    """
    gets user's followed threads
    """
    r = redis.Redis(db=LCDB)
    return [int(tid) for tid in r.smembers('u:foll:'+str(uid))]


# tested
def get_user_notif_count(uid):
    r = redis.Redis(db=LCDB)
    return r.zcard('u:notif:'+str(uid))


# tested
def get_user_notifs(uid):
    r = redis.Redis(db=LCDB)
    return [msgpack.unpackb(notif) for notif in r.zrange('u:notif:'+str(uid),0,-1)]


# tested
def get_user_notifs_after(uid,time):
    """
    gets notifications created after <time>
    """
    r = redis.Redis(db=LCDB)
    return [msgpack.unpackb(notif) for notif in r.zrange('u:notif:'+str(uid),int(time),-1)]


def delete_notifs(uid,times):
    """
    deletes notifs with given <times> timestamps
    """
    r = redis.Redis(db=LCDB)
    for time in times:
        r.zremrange('u:notif:'+str(uid),int(time),int(time))


def delete_all_notifs(uid):
    r = redis.Redis(db=LCDB)
    r.delete('u:notif:'+str(uid))


# tested
def follow_thread(uid,tid,follow):
    r = redis.Redis(db=LCDB)
    if not follow:
        r.srem('u:foll:'+str(uid),str(tid))
        r.srem('t:foll:'+str(tid),str(uid))
    else:
        r.sadd('u:foll:'+str(uid),str(tid))
        r.sadd('t:foll:'+str(tid),str(uid))


# tested
def is_following(uid,tids):
    r = redis.Redis(db=LCDB)
    return [r.sismember('u:foll:'+str(uid),str(tid)) for tid in tids]


# tested
def vote(uid,cid,vote):
    r = redis.Redis(db=LCDB)
    if r.sismember('u:up:'+str(uid),str(cid)):
        if vote == 1:
            return
        else:
            r.srem('u:up:'+str(uid),str(cid))
            r.decr('c:up:'+str(cid))
    elif r.sismember('u:down:'+str(uid),str(cid)):
        if vote == -1:
            return
        else:
            r.srem('u:down:'+str(uid),str(cid))
            r.decr('c:down:'+str(cid))
    if vote == 1:
        r.sadd('u:up:'+str(uid),cid)
        r.incr('c:up:'+str(cid))
    elif vote == -1:
        r.sadd('u:down:'+str(uid),cid)
        r.incr('c:down:'+str(cid))


# tested
def did_vote(uid,cids):
    """
    returns a list of 0:not-voted, 1:up-voted, -1:down-voted for given comment_ids and user_id
    """
    r = redis.Redis(db=LCDB)
    votes = []
    for cid in cids:
        if r.sismember('u:up:'+str(uid),str(cid)):
            votes.append(1)
        elif r.sismember('u:down:'+str(uid),str(cid)):
            votes.append(-1)
        else:
            votes.append(0)
    return votes


# tested
def add_comment(tid,cid,text,parent=-1):
    """
    adds given comment to thread - notifies the followers and the parent commentor - returns comment_id
    """
    r = redis.Redis(db=LCDB)
    cname = r.get('u:'+str(cid))
    if cname == None:
        return (False,'Creator does not exist')
    parent_comment = None
    if parent != -1:
        parent_comment = get_comments([parent])[0]
        if parent_comment == None:
            return (False,'Parent comment does not exist')

    comment_id = generate_id()
    timestamp = int(time())
    comment_dict = {
        'text':text,
        'time':timestamp,
        'pid':parent,
        'cid':cid,
        'cname':cname
        }
    r.set('c:'+str(comment_id),msgpack.packb(comment_dict))
    r.lpush('t:comm:'+str(tid),comment_id)
    r.lpush('u:comm:'+str(cid),comment_id)
    notified = [cid]
    if parent_comment != None:
        parent_creator = int(parent_comment['cid'])
        if parent_creator not in notified:
            notified.append(parent_creator)
            reply_notification = {
                'tid':tid,
                'cid':cid,
                'type':1
                }
            r.zadd('u:notif:'+str(parent_creator),msgpack.packb(reply_notification),timestamp)
    notification = {
        'tid':tid,
        'cid':cid,
        'type':0
        }
    for f in r.smembers('t:foll:'+str(tid)):
        if int(f) not in notified:
            notified.append(int(f))
            r.zadd('u:notif:'+str(f),msgpack.packb(notification),timestamp)
    return (True,comment_id)


# tested
def get_thread_comments(tid):
    """
    returns the comment ids of a given thread
    """
    r = redis.Redis(db = LCDB)
    return [int(cid) for cid in r.lrange('t:comm:'+str(tid),0,-1)]


# tested
def get_comments(cids):
    """
    returns comments with ids [cids] adds total up and down-votes on the fly
    """
    r = redis.Redis(db = LCDB)
    pipe = r.pipeline()
    for cid in cids:
        pipe.get('c:'+str(cid))
    comments = pipe.execute()
    for ind,c in enumerate(comments):
        if c != None:
            comments[ind] = msgpack.unpackb(c)
            up = r.get('c:up:'+str(cids[ind]))
            if up:
                comments[ind]['up'] = int(up)
            else:
                comments[ind]['up'] = 0
            down = r.get('c:down:'+str(cids[ind]))
            if up:
                comments[ind]['down'] = int(down)
            else:
                comments[ind]['down'] = 0
 
    return comments


# tested
def get_thread_headers(tids):
    """
    returns threads with ids [tids] adds the tags on the fly as a list of dict [{'id':<tagid>,'name':<tagname>}]
    """
    r = redis.Redis(db = LCDB)
    pipe = r.pipeline()
    for tid in tids:
        pipe.get('t:'+str(tid))
    headers = pipe.execute()
    for ind,h in enumerate(headers):
        if h != None:
            headers[ind] = msgpack.unpackb(h)
            tid = tids[ind]
            tags = r.lrange('t:tags:'+str(tid),0,-1)
            tag_dicts = []
            for tagid in tags:
                tag_dicts.append((tagid,r.get('tag:'+str(tagid))))
            headers[ind]['tags'] = tag_dicts
            headers[ind]['num_comment'] = r.llen('t:comm:'+str(tid))
            headers[ind]['id'] = tid
    return headers


# tested
def get_tags():
    """
    returns all available tags sorted by number of usages [(id,name,usage)]
    """
    r = redis.Redis(db = LCDB)
    tags = r.keys('tag:t:*')
    out = []
    for t in tags:
        tagid = int(t.split(':')[2])
        tagname = r.get('tag:'+str(tagid))
        num_used = r.llen(t)
        out.append((tagid,tagname,num_used))
    out = sorted(out, key = lambda x : x[2])
    out.reverse()
    return out


# tested
def get_threads_with_tag(tagid):
    """
    returns the threads tagged with given tag
    """
    r = redis.Redis(db = LCDB)
    return [int(tid) for tid in r.lrange('tag:t:'+str(tagid),0,-1)]


# tested
def get_tags_by_id(tagids):
    """
    given list of tag ids - returns tag names
    """
    r = redis.Redis(db = LCDB)
    return [r.get('tag:'+str(tagid)) for tagid in tagids]


# tested
def get_tags_by_name(tagnames):
    """
    given list of tag names return tag ids - creates tags if necessary
    """
    r = redis.Redis(db = LCDB)
    tagids = [] 
    for tagname in tagnames:
        tagid = r.get('tag:'+str(tagname))
        if tagid == None:
            # create tag here
            tagid = generate_id()
            r.set('tag:'+str(tagname),tagid)
            r.set('tag:'+str(tagid),tagname)
        tagids.append(tagid)
    return tagids


# tested
def add_tags(tid,tags):
    """
    tags the thread with given tagids
    """
    r = redis.Redis(db = LCDB)
    for tagid in tags:
        r.lpush('tag:t:'+str(tagid),tid)
        r.lpush('t:tags:'+str(tid),tagid)


def create_thread(title,url,domain,cid,tags=[],summary=''):
    """
    creates a thread and returns the thread id
    tags is a list of tag-ids, the tags should be created (if not existent) prior to calling this function
    """
    r = redis.Redis(db = LCDB)
    cname = r.get('u:'+str(cid))
    if cname == None:
        return (False,'Creator not found')
    tid = generate_id()
    thread_header = {
        'title':title,
        'summary':summary,
        'url':url,
        'domain':domain,
        'time':int(time()),
        'cid':cid,
        'cname':cname
        }
    for tagid in tags:
        r.lpush('t:tags:'+str(tid),tagid)
        r.lpush('tag:t:'+str(tagid),tid)
    r.set('t:'+str(tid),msgpack.packb(thread_header))
    return (True,tid)


# tested
def generate_id():
    return int(os.urandom(4).encode('hex'),16) / 2


# tested
def swap_user_info(u):
    """
    given user id returns username or vice versa
    """
    r = redis.Redis(db = LCDB)
    return r.get('u:'+str(u))
