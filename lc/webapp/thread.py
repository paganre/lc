from webapp.models import Thread,Domain,LcUser,Comment
from webapp import comment as c
from webapp.struct.subthread import Subthread
from django.db import connection
from time import time
import traceback
import os

def generateId():
    return int(os.urandom(4).encode('hex'),16) / 2

def get_full_thread(tid):
    try:
        t = Thread.objects.get(pk = int(tid))
        all_comments = Comment.objects.filter(thread = t).order_by('time_created') # old-to-new ordering: should preserve subthreading logic
        subs = []
        # create the subthread trees here
        for c in all_comments:
            if c.parent == None:
                subs.append(Subthread(c,[]))
            else:
                for s in subs:
                    if(s.insertChildTo(c.parent.id,Subthread(c,[]))):
                        break

        # convert trees to traversed lists
        comments = []
        for s in subs:
            comments.append(s.toList(0,[]))

        return (True,{'id':t.id,
                      'url':t.url,
                      'title':t.title,
                      'domain':t.domain.name,
                      'creator_name':t.creator.user.username,
                      'creator_id':t.creator.id,
                      'net_vote':t.up-t.down,
                      'time':t.time_created,
                      'num_comment':len(Comment.objects.filter(thread = t)),
                      },comments)
    except:
        connection._rollback()
        return (False,str(traceback.format_exc()))

def get_thread_header(tid):
    try:
        t = Thread.objects.get(pk = int(tid))
        return (True,{'id':t.id,
                      'url':t.url,
                      'title':t.title,
                      'domain':t.domain.name,
                      'creator_name':t.creator.user.username,
                      'creator_id':t.creator.id,
                      'net_vote':t.up-t.down,
                      'time':t.time_created,
                      'num_comment':len(Comment.objects.filter(thread = t))})
    except:
        connection._rollback()
        return (False,str(traceback.format_exc()))

def create_thread(creator_id, title, suggested_title, domain, url):
    try:
        # retrieve LcUser
        creator = LcUser.objects.get(pk = creator_id)
        tid = generateId()
        t = Thread(id=tid,
                   creator=creator,
                   title=title,
                   suggested_title=suggested_title,
                   url = url,
                   domain = domain,
                   time_created = int(time()))
        t.save()
        return (True,tid) # thread created - return thread id
    except:
        connection._rollback()
        return (False,str(traceback.format_exc()))        
