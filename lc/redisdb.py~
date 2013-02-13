import redis
import msgpack
import os
from time import time

"""
Redis Structures:
-----------------
 Thread-Lists:
  act:ids          list of active ids in a time-sorted manner
  act:sorted:ids   list of active ids in an algorithm-sorted manner
 Threads:
  t:<tid>          msgpacked thread-header of thread (see: aux-structures)
  t:tags:<tid>     list of tag-ids for thread
  t:comm:<tid>     list of comment-ids for thread in a time-sorted manner
  t:foll:<tid>     set of followers of the thread
 Tags:
  tag:<tagid>      name of the tag
  tag:<tagname>    id of the tag
  tag:t:<tagid>    thread list of the tags in a time-sorted manner
 Comments:
  c:<cid>          msgpacked comment (see:aux-structures)
  c:up:<cid>       up-votes of comment
  c:down:<cid>     down-votes of comment
 Users:
  u:<uid>          username of user
  u:<uname>        id of user
  u:comm:<uid>     comment-list of user
  u:up:<uid>       user's up-voted comment set
  u:down:<uid>     user's down-voted comment set
  u:auth:<uid>     user's state token - expiry
  auth:<state>     user id for given state token
  u:pass:<uid>     user's password
  u:time:<uid>     user's time of join
  u:foll:<uid>     set of thread-id's that user is following
  u:notif:<uid>    sorted-set of notifications for user with score = timestamp (see: aux-structures)  

Aux Structures:
---------------
 thread-header: {title,summary,url,domain,time,cid,cname}
 comment: {text,time,pid,cid,cname} [pid is parent id it's either -1 or a comment id]
 notification: {tid,cid,type} [type is either 1 (reply) or 0 (follow-notif)]

"""

THREAD_PER_PAGE = 25

def get_thread_ids(page = 0, algoritm = False):
    """
    thread id pagination, if algo = False returns time-sorted
    """
    r = redis.Redis()
    if algorithm:
        return r.lrange('act:sorted:ids',page*THREAD_PER_PAGE, (page+1)*THREAD_PER_PAGE -1)
    return r.lrange('act:ids',page*THREAD_PER_PAGE, (page+1)*THREAD_PER_PAGE-1)


def get_user_comments(uid):
    r = redis.Redis()
    return [int(cid) for cid in r.lrange('u:comm:'+str(uid))]


def get_user_follows(uid):
    """
    gets user's followed threads
    """
    r = redis.Redis()
    return [int(tid) for tid in r.smembers('u:foll:'+str(uid))]


def get_user_notif_count(uid):
    r = redis.Redis()
    return r.zcard('u:notif:'+str(uid))


def get_user_notifs(uid):
    r = redis.Redis()
    return [msgpack.unpackb(notif) for notif in r.zrange('u:notif:'+str(uid),0,-1)]


def get_user_notifs_after(uid,time):
    """
    gets notifications created after <time>
    """
    r = redis.Redis()
    return [msgpack.unpackb(notif) for notif in r.zrange('u:notif:'+str(uid),int(time),-1)]


def delete_notifs(uid,times):
    """
    deletes notifs with given <times> timestamps
    """
    r = redis.Redis()
    for time in times:
        r.zremrange('u:notif:'+str(uid),int(time),int(time))


def delete_all_notifs(uid):
    r = redis.Redis()
    r.delete('u:notif:'+str(uid))


def follow_thread(uid,tid,follow):
    r = redis.Redis()
    if not follow:
        r.srem('u:foll:'+str(uid),str(tid))
        r.srem('t:foll:'+str(tid),str(uid))
    else:
        r.sadd('u:foll:'+str(uid),str(tid))
        r.sadd('t:foll:'+str(tid),str(uid))


def is_following(uid,tids):
    r = redis.Redis()
    return [r.sismember('u:foll:'+str(uid),str(tid)) for tid in tids]


def vote(uid,cid,vote):
    r = redis.Redis()
    if r.sismember('u:up:'str(uid),str(cid))
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


def did_vote(uid,cids):
    """
    returns a list of 0:not-voted, 1:up-voted, -1:down-voted for given comment_ids and user_id
    """
    r = redis.Redis()
    votes = []
    for cid in cids:
        if r.sismember('u:up:'+str(uid),str(cid)):
            votes.append(1)
        elif r.sismember('u:down:'+str(uid),str(cid)):
            votes.append(-1)
        else:
            votes.append(0)
    return votes


def add_comment(tid,cid,text,parent=-1):
    """
    adds given comment to thread - notifies the followers and the parent commentor - returns comment_id
    """
    r = redis.Redis()
    cname = r.get('u:'+str(cid))
    if cname == None:
        return (False,'Creator does not exist')
    parent_comment = None
    if parent != -1:
        parent_comment = get_comments([parent])
        if len(parent_comment) == 0:
            return (False,'Parent comment does not exist')
        parent_comment = parent_comment[0]

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
    for follower in r.smembers('t:foll:'+str(tid)):
        if int(f) not in notified:
            notified.append(int(f))
            r.zadd('u:notif:'+str(f),msgpack.packb(notification),timestamp)
    return (True,comment_id)


def get_comments(cids):
    """
    returns comments with ids [cids] adds total up and down-votes on the fly
    """
    r = redis.Redis()
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


def get_thread_headers(tids):
    """
    returns threads with ids [tids] adds the tags on the fly as a list of dict [{'id':<tagid>,'name':<tagname>}]
    """
    r = redis.Redis()
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
                tag_dicts.append({'id':tagid,'name':r.get('tag:'+str(tagid))})
            headers[ind]['tags'] = tag_dicts
    return headers


def get_tags():
    """
    returns all available tags sorted by number of usages [(id,name,usage)]
    """
    r = redis.Redis()
    tags = r.keys('tag:t:*')
    out = []
    for t in tags:
        tagid = int(t.split(':')[2])
        tagname = r.get('tag:'+str(tagid))
        num_used = r.llen(t)
        out.append(tagid,tagname,num_used)
    return out


def get_tags_by_id(tagids):
    """
    given list of tag ids - returns tag names
    """
    r = redis.Redis()
    return [r.get('tag:'+str(tagid)) for tagid in tagids]


def get_tags_by_name(tagnames):
    """
    given list of tag names return tag ids - creates tags if necessary
    """
    r = redis.Redis()
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


def add_tags(tid,tags):
    """
    tags the thread with given tagids
    """
    r = redis.Redis()
    for tagid in tags:
        r.lpush('tags:t:'+str(tagid),tid)
        r.lpush('t:tags:'+str(tid),tagid)


def create_thread(title,url,domain,cid,tags=[],summary=''):
    """
    creates a thread and returns the thread id
    tags is a list of tag-ids, the tags should be created (if not existent) prior to calling this function
    """
    r = redis.Redis()
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

def generate_id():
    return int(os.urandom(4).encode('hex'),16) / 2


def generate_state():
    return os.urandom(16).encode('hex')


def register_user(username,password):
    """
    register returns (userid,state)
    """
    # check if user exists
    r = redis.Redis()
    if (r.get('u:'+username)):
        return (False,'User exists')
    # create user
    uid = generate_id()
    state = generate_state()

    r.set('u:'+username,uid)
    r.set('u:'+str(uid),username)
    r.set('u:pass:'+str(uid),password)
    r.set('u:time:'+str(uid),int(time()))
    
    r.set('u:auth:'+str(uid),state)
    r.set('auth:'+state,uid)
    
    return (True,(uid,state))


def login(username,password):
    """
    Login returns (userid,state)
    """
    r = redis.Redis()
    uid = r.get('u:'+username)
    if uid == None:
        return (False,'Wrong username or password')
    if r.get('u:pass'+str(uid)) != password:
        return (False,'Wrong username or password')
    state = r.get('u:auth:'+str(uid))
    if state == None:
        state = generate_state()
        r.set('u:auth:'+str(uid),state)
        r.set('auth:'+state,uid)
    return (True,(uid,state))


def validate_state(uid,state):
    """
    checks if given user id and state pair is correct
    """
    r = redis.Redis()
    uid_ = r.get('auth:'+state)
    state_ = r.get('u:auth:'+str(uid))
    if uid_ == None:
        return False
    return int(uid_) == int(uid) and state == state_
    

def get_user_info(uid):
    """
    given user id returns (username,state)
    """
    r = redis.Redis()
    return (r.get('u:'+str(uid)),r.get('u:auth:'+str(uid)))
