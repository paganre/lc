from webapp.models import Thread,Domain,LcUser,Comment
from django.db import connection
from time import time
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
        c = Comment(id = id, creator=creator, thread = thread, parent = parent, text=text, time_created = int(time()))
        c.save()
        return (True,id)
    except:
        connection._rollback()
        return (False,str(traceback.format_exc()))

def get_comment(cid):
    try:
        comment = Comment.objects.get(pk = int(cid))
        return (True,{'id':comment.id,
                      'creator_name':comment.creator.user.username,
                      'creator_id':comment.creator.id,
                      'time':comment.time_created,
                      'text':comment.text,
                      'net_vote':comment.up-comment.down})
    except:
        connection._rollback()
        return (False,str(traceback.format_exc()))

def comment_to_dict(comment):
    return {'id':comment.id,
            'creator_name':comment.creator.user.username,
            'creator_id':comment.creator.id,
            'text':comment.text,
            'time':comment.time_created,
            'net_vote':comment.up-comment.down}

def get_comment_fields(subthread):
    """
    aux function to return the extracted fields of a comment subthread
    """
    out = []
    for comment in subthread:
        out.append({'id':comment.id,
                    'creator_name':comment.creator.user.username,
                    'creator_id':comment.creator.id,
                    'time':comment.time_created,
                    'text':comment.text,
                    'net_vote':comment.up-comment.down})
    return out
