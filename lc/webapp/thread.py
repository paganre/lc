from webapp.models import Thread,Domain,LcUser,Comment
from webapp.struct.subthread import Subthread
import msgpack
from django.db import connection
from time import time
import traceback
import os
from django.db.models import F
from webapp import alfred
from webapp import tagger
from webapp.pretty_time import pretty_time
import redis
import msgpack

LCDB = 1

def generateId():
    return int(os.urandom(4).encode('hex'),16) / 2

def increment_view_count(tid):
    try:
        Thread.objects.filter(pk = int(tid)).update(views = F('views')+1)
        return True
    except:
        return False

def get_full_thread(tid):
    try:
        t = Thread.objects.get(pk = int(tid))
        all_comments = Comment.objects.filter(thread = t).order_by('time_created') # old-to-new ordering: should preserve subthreading logic
        ids = []
        subs = []
        # create the subthread trees here
        for c in all_comments:
            ids.append(c.id)
            if c.parent == None:
                subs.append(Subthread(c,[]))
            else:
                for s in subs:
                    if(s.insertChildTo(c.parent.id,Subthread(c,[]))):
                        break

        if not alfred.subthread_list_sort(subs):
            return (False,str(traceback.format_exc()))
        # convert trees to traversed lists
        comments = []
        for s in subs:
            comments.append(s.toList(0,[]))

        return (True,{'id':t.id,
                      'url':t.url,
                      'title':t.title,
                      'summary':t.summary,
                      'domain':t.domain.name,
                      'creator_name':t.creator.user.username,
                      'creator_id':t.creator.id,
                      'net_vote':t.up-t.down,
                      'time':pretty_time(int(t.time_created)),
                      'num_comment':len(Comment.objects.filter(thread = t)),
                      'tags':tagger.get_tags(int(tid))
                      },comments,ids)
    except:
        connection._rollback()
        return (False,str(traceback.format_exc()))

def get_thread_header(tid):
    try:
        # check cache
        
        t = Thread.objects.get(pk = int(tid))
        return (True,{'id':t.id,
                      'url':t.url,
                      'title':t.title,
                      'summary':t.summary,
                      'domain':t.domain.name,
                      'creator_name':t.creator.user.username,
                      'creator_id':t.creator.id,
                      'net_vote':t.up-t.down,
                      'time':pretty_time(int(t.time_created)),
                      'tags':tagger.get_tags(int(tid)),
                      'num_comment':len(Comment.objects.filter(thread = t))})
    except:
        connection._rollback()
        return (False,str(traceback.format_exc()))

def create_thread(creator_id, title,summary, suggested_title, domain, url):
    try:
        # retrieve LcUser
        creator = LcUser.objects.get(pk = creator_id)
        tid = generateId()
        t = Thread(id=tid,
                   creator=creator,
                   title=title,
                   summary=summary,
                   suggested_title=suggested_title,
                   url = url,
                   domain = domain,
                   time_created = int(time()))
        t.save()
        # add to act:ids
        r = redis.Redis(db = LCDB)
        r.lpush('act:ids',tid)
        return (True,tid) # thread created - return thread id
    except:
        connection._rollback()
        return (False,str(traceback.format_exc()))

def check_domain_stitle(sugg_title, dom):
    qSetCard = Thread.objects.filter(suggested_title = sugg_title, domain = dom).count()
    if qSetCard == 1:
        return (qSetCard, Thread.objects.get(suggested_title = sugg_title, domain = dom).id)
    else:
        return (qSetCard, 0)
