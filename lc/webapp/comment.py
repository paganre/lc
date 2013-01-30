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
        if(parent != None):
            parent = Comment.objects.get(pk = int(parent))
        c = Comment(id = id, creator=creator, thread = thread,parent = parent, time_created = int(time()))
        c.save()
        return (True,id)
    except:
        return (False,str(traceback.format_exc()))
        
