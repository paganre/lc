from django.core.exceptions import ObjectDoesNotExist
from webapp.models import Thread,Comment,Tag,Domain,LcUser
from django.core.cache import cache
from time import time
import redis
import msgpack
import traceback
from webapp import alfred


def get_active_ids():
    """
    returns a list of all active IDs
    IDs are obtained from Redis via get('act:ids')
    """
    r = redis.Redis()
    pipe = r.pipeline()
    pipe.get('act:ids')
    results = pipe.execute()
    try:
        active_ids = msgpack.unpackb(results[0],use_list = 1)
        return active_ids
    except:
        return []


def get_thread_ids_with_tag(tagid):
    """
    returns a list of active thread ids tagged with tagid 
    """
    r = redis.Redis()
    tids = r.lrange('tags:t:'+str(tagid),0,-1)
    return [int(tid) for tid in tids]


def get_tags_by_name(tag_names):
    """
    returns {'tag:<tagname>':<tagid>} dict
    """
    try:
        # check cache
        tags = cache.get_many(['tag:'+str(tag_name) for tag_name in tag_names])
        for tag_name in tag_names:
            if 'tag:'+str(tag_name) not in tags:
                # cahce miss
                try:
                    tag = Tag.objects.get(name = tag_name)
                    # cache result
                    cache.set('tag:'+tag.name,tag.id)
                    cache.set('tag:'+str(tag.id),tag.name)
                    tags['tag:'+str(tag_name)] = tag.id
                except ObjectDoesNotExist:
                    # tag does not exist
                    continue
        return tags
    except:
        print traceback.format_exc()
        return []

def add_tag_to_thread(tid,tag_name):
    """
    tags the given thread with given tag - creates tag if necessary
    """
    try:
        if tid not in get_active_ids():
            return (False,'Thread not active')
        tag_result = get_tags_by_name([tag_name])
        if len(tag_result) == 0:
            # tag does not exist - create it
            
    
def get_tags_by_id(tag_ids):
    """
    returns {'tag:<tagid>':<tagname>} dict
    """
    try:
        # check cache
        tags = cache.get_many(['tag:'+str(tagid) for tagid in tag_ids])
        for tagid in tag_ids:
            if 'tag:'+str(tagid) not in tags:
                # cache miss
                try:
                    tag = Tag.objects.get(pk = tagid)
                    # cache result
                    cache.set('tag:'+str(tag.id),tag.name)
                    cache.set('tag:'+tag.name,tag.id)
                    tags['tag:'+str(tagid)] = tag.name
                except ObjectDoesNotExist:
                    # tag does not exist
                    continue
        return tags
    except:
        print traceback.format_exc()
        return []


def get_thread_headers(tids):
    """
    returns the thread headers for given thread ids
    Thread headers in the cache will hold:
    id, url, title, summary, domain, cname, cid, time
    following will be acquired thru redis:
    tag-ids:             lrange('t:tags:<tid>',0,-1)
    number-of-comments:  llen('t:comms:<tid>')
    net-vote:            get('t:up:<tid>') - get('t:down:<tid>')
    """
    try:
        # check cache
        headers = cache.get_many(['t:head:'+str(tid) for tid in tids])
        r = redis.Redis()
        pipe = r.pipeline()
        for tid in tids:
            pipe.lrange('t:tags:'+str(tid),0,-1)
            pipe.llen('t:comms:'+str(tid))
            pipe.get('t:up:'+str(tid))
            pipe.get('t:down:'+str(tid))
        results = pipe.execute()
        for i,tid in enumerate(tids):
            # get cache misses from db and cache them
            if 't:head:'+str(tid) not in headers:
                # cache miss
                try:
                    t = Thread.objects.get(pk = tid)
                    tdict = {
                        'id':t.id,
                        'url':t.url,
                        'title':t.title,
                        'summary':t.summary,
                        'domain':t.domain.name,
                        'cname':t.creator.user.username,
                        'cid':t.creator.id,
                        'time':t.time_created
                        }
                    cache.set('t:head:'+str(tid),msgpack.packb(tdict))
                    headers['t:head:'+str(tid)] = tdict
                except ObjectDoesNotExist:
                    # thread does not exist
                    continue
            else:
                headers['t:head:'+str(tid)] = msgpack.unpackb(headers['t:head:'+str(tid)]) #unpack the result obtain from cache
            headers['t:head:'+str(tid)]['tags'] = get_tags_by_id(results[i*4]) # list of tag names
            headers['t:head:'+str(tid)]['numcom'] = results[i*4+1]
            if results[i*4+2] == None:
                results[i*4+2] = 0
            if results[i*4+3] == None:
                results[i*4+3] = 0
            headers['t:head:'+str(tid)]['netvote'] = int(results[i*4+2]) - int(results[i*4+3])
        return headers
    except:
        print traceback.format_exc()
        return []
