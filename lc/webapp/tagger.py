from webapp.models import Thread,Tag,LcUser
from django.db import connection
import traceback
import os
from time import time

def generateId():
    return int(os.urandom(4).encode('hex'),16) / 2

def get_tags(tid):
    """
    returns tag info [ (tag_id, tag_name) ] for given thread id
    """
    try:
        tags = Tag.objects.filter(threads__in=[Thread.objects.get(pk = int(tid))])
        out = []
        for t in tags:
            out.append((t.id,t.name))
        return out
    except:
        return []

def get_threads(tagid):
    try:
        threads = Tag.objects.get(id=int(tagid)).threads.all()
        tids = [t.id for t in threads]
        return tids
    except:
        return []


def tag(uid,tid,tagname):
    """
    tags the thread with given tagname - only creator of the thread can do it for now
    """
    try:
        t = Thread.objects.get(pk = int(tid))
        if t.creator.id != int(uid):
            return (False,'kendi postlarini etiketle bence')
        
        tagname = tagname.strip().lower()
        if tagname.startswith('#'):
            tagname = tagname[1:]
        if '#' in tagname:
            return (False,'boyle etiket olmaz ki')
        if ' ' in tagname:
            return (False,'etiketlerde bosluk olmuyo')

        tag = Tag.objects.filter(name = tagname)
        if len(tag) == 0:
            id = generateId()
            tag = Tag(id = id, name = tagname)
            tag.save()
            tag.threads.add(t)
            tag.save()
            return (True,'')
        else:
            tag = tag[0]
            if len(tag.threads.filter(id = t.id)) != 0:
                return (False,'bu etiket varmis ki bunda')
            else:
                tag.threads.add(t)
                tag.save()
                return (True,'')
    except:
        connection._rollback()
        return (False,str(traceback.format_exc()))
