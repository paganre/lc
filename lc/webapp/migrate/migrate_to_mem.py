from webapp.models import Thread, Comment, Tag
from django.core.cache import cache
from time import time
import msgpack
import redis


def migrate_threads_to_redis():
    """
    Gets all threads from PostGres and creates:
    1- act:ids
    2- t:<tid> hash-sets
    3- tag:<tagid>:news sets
    in redis
    """
    r = redis.Redis()
    pipe = r.pipeline()
    # clear possible prior data
    pipe.delete('act:ids')
    pipe.delete('act:sorted:ids')
    for t in r.keys('t:*'):
        pipe.delete(t)
    for tag in r.keys('tag:*:news'):
        pipe.delete(tag)
    pipe.execute()
    # get all threads in db
    act_ids = []
    for t in Thread.objects.all().order_by('-time_created'):
        act_ids.append(t.id)
        hash_set = {
            'view':t.views,
            'comms':Comment.objects.filter(thread = t).count(),
            'up':t.up,
            'down':t.down,
            'time':t.time_created
            }
        pipe.hmset('t:'+str(t.id),hash_set)
    pipe.set('act:ids',msgpack.packb(act_ids))
    for tag in Tag.objects.all():
        threads = tag.threads.all()
        for t in threads:
            pipe.sadd('tag:'+str(tag.id)+':news',t.id)
    pipe.execute()


def populate_cache():
    """
    resource cache structures:
    1-Thread Header
    t:head:<tid> => {title,summary,cid,cname,url,domain}
    2-Thread Comments List
    t:comm:<tid> => [comment_ids]
    3-Thread Tag List
    t:tags:<tid> => [tag_ids]
    4-Comments
    c:<cid> => {cid,cname,text,time,parent}
    5-Tags
    tag:<tagid> => name
    """
    # clear possible prior data
    cache.clear()
    r = redis.Redis()
    act_ids = msgpack.unpackb(r.get('act:ids'),use_list = 1)
    for id in act_ids:
        t = Thread.objects.get(pk = id)
        # set the thread headers
        tdict = {'title':t.title,'summary':t.summary,'cid':t.creator.id,'cname':t.creator.user.username,'url':t.url,'domain':t.domain.name}
        cache.set('t:head:'+str(t.id),msgpack.packb(tdict))
        # set the comment id list in an time-ordered manner (old to new)
        comments = Comment.objects.filter(thread = t).order_by('time_created')
        cache.set('t:comm:'+str(t.id),msgpack.packb([c.id for c in comments]))
        # set comment cache
        for c in comments:
            parent = -1
            if c.parent:
                parent = c.parent.id
            cdict = {
                'cid':c.creator.id,
                'cname':c.creator.user.username,
                'ctext':c.text,
                'time':c.time_created,
                'parent':parent
                }
            cache.set('c:'+str(c.id),msgpack.packb(cdict))
        # set thread tags cache
        tags = [(tag.id,tag.name) for tag in t.tag_set.all()]
        cache.set('t:tags:'+str(t.id),msgpack.packb([tag[0] for tag in tags]))
        # set tag cache - never gets invalidated
        for tag in tags:
            cache.set('tag:'+str(tag[0]),tag[1])
        
