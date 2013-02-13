from webapp.models import Thread, Comment, Tag, LcUser
from django.core.cache import cache
from time import time
import msgpack
import redis


MDB = 1


def migrate_threads_to_redis():
    """
    Creates the Redis Structures described in webapp/redisdb.py
    """
    r = redis.Redis(db = MDB)
    r.flushdb() # clear or prior data

    # get all threads in db
    for t in Thread.objects.all().order_by('-time_created'):
        r.lpush('act:ids',t.id)
        tdict = {
            'title':t.title,
            'summary':t.summary,
            'url':t.url,
            'domain':t.domain.name,
            'time':t.time_created,
            'cid':t.creator.id,
            'cname':t.creator.user.username
            }
        r.set('t:'+str(t.id),msgpack.packb(tdict))
        for tag in t.tag_set.all():
            tagid = tag.id
            tagname = tag.name
            r.set('tag:'+str(tagid),tag.name)
            r.set('tag:'+tagname,tagid)
            r.lpush('t:tags:'+str(t.id),tagid)
            r.lpush('tag:t:'+str(tagid),t.id)
        for comment in Comment.objects.filter(thread = t).order_by('-time_created'):
            r.lpush('t:comm:'+str(t.id),comment.id)
            r.lpush('u:comm:'+str(comment.creator.id),comment.id)
            pid = -1
            if comment.parent:
                pid = comment.parent.id
            cdict = {
                'text':comment.text,
                'time':comment.time_created,
                'pid': pid,
                'cid':comment.creator.id,
                'cname':comment.creator.user.username
                }
            r.set('c:'+str(comment.id),msgpack.packb(cdict))

    for u in LcUser.objects.all():
        r.set('u:'+str(u.id),u.user.username)
        r.set('u:'+u.user.username,u.id)
        r.set('u:time:'+str(u.id),u.time_joined)
