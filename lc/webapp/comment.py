from webapp.models import Thread,Domain,LcUser,Comment
from webapp import user as u
from django.db import connection
from time import time
from webapp.pretty_time import pretty_time
from django.core.cache import cache
import msgpack
import traceback
import os

def generateId():
    return int(os.urandom(4).encode('hex'),16) / 2

def add_comment(uid,tid,text,parent=None):
    try:
        id = generateId()
        creator = LcUser.objects.get(pk = int(uid))
        thread = Thread.objects.get(pk = int(tid))
        if (parent != None):
            parent = Comment.objects.get(pk = int(parent))
        timestamp = int(time())
        c = Comment(id = id, creator=creator, thread = thread, parent = parent, text=text, time_created = timestamp)
        c.save()
        notified = [creator.id]
        if (parent != None):
            if parent.creator.id != creator.id:
                u.notify(parent.creator.id,c.id,True)
                notified.append(parent.creator.id)

        followers = u.get_followers(int(tid))
        
        for f in followers:
            if f not in notified:
                u.notify(f,c.id,False)
    
        p = -1
        if parent:
            p = parent.id
        
        return (True,id)
    except:
        connection._rollback()
        return (False,str(traceback.format_exc()))

def comment_to_dict(comment):
    return {'id':comment.id,
            'creator_name':comment.creator.user.username,
            'creator_id':comment.creator.id,
            'text':comment.text,
            'time':pretty_time(int(comment.time_created)),
            'net_vote':comment.up-comment.down}

def get_comment(cid):
    try:
        comment = Comment.objects.get(pk = int(cid))
        return (True,comment_to_dict(comment))
    except:
        connection._rollback()
        return (False,str(traceback.format_exc()))


def get_comment_fields(subthread):
    """
    aux function to return the extracted fields of a comment subthread
    """
    out = []
    for comment in subthread:
        out.append({'id':comment.id,
                    'creator_name':comment.creator.user.username,
                    'creator_id':comment.creator.id,
                    'time':pretty_time(int(comment.time_created)),
                    'text':comment.text,
                    'net_vote':comment.up-comment.down})
    return out
