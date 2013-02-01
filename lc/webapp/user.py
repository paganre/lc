from django.contrib.auth.models import User
from webapp.models import LcUser,Comment
from django.db import connection
from time import time
from django.contrib import auth
import traceback
import os
import redis
from django.db.models import F

def notify(uid,cid):
    """
    notify user about a reply to his-her comment from another user
    """
    try:
        r = redis.Redis()
        r.zadd('not:'+str(uid),str(cid),int(time()))
    except:
        return None # fail silent - not a big deal

def get_notifs(uid):
    try:
        r = redis.Redis()
        notifs = r.zrange('not:'+str(uid),0,-1,withscores=True)
        return notifs
    except:
        return []

def del_notif(uid,cid):
    try:
        r = redis.Redis()
        r.zrem('not:'+str(uid),str(cid))
    except:
        return None

def did_vote(uid,cids):
    """
    returns -1,0,1 for downvote,notvoted,upvote for given u(ser)id and c(omment)ids
    """
    try:
        r = redis.Redis()
        votes = r.hmget('v:'+str(uid),[str(cid) for cid in cids])
        out = []
        for vote in votes:
            if vote == None:
                out.append(0)
            else:
                out.append(int(vote))
        return (True,out)
    except:
        return (False,str(traceback.format_exc()))
        
def vote(uid,cid,vote):
    """
    add user vote (! changes both redis and postgres !)
    """
    try:
        r = redis.Redis()
        v = r.hget('v:'+str(uid),str(cid))
        if v == None:
            v = 0
        else:
            v = int(v)
        if v == vote:
            return (True,'') # no need to change - same vote - should never be possible
        r.hset('v:'+str(uid),str(cid),vote)
        
        c = Comment.objects.get(pk = int(cid))
        t = c.thread

        if v == 1:
            c.up = c.up - 1
            t.up = t.up - 1
        elif v == -1:
            c.down = c.down - 1
            t.down = t.down - 1
        if vote == 1:
            c.up = c.up + 1
            t.up = t.up + 1
        elif vote == -1:
            c.down = c.down +1
            t.down = t.down +1

        c.save()
        t.save()

        return (True,'')
    except:
        connection._rollback()
        return (False,str(traceback.format_exc()))

def login(request,username,password):
    try:
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user);
            # bring up associated lc-user object
            lcuser = LcUser.objects.get(user = user)
            request.session['uid'] = lcuser.id
            return (True,'')
        return (False,'')
    except:
        connection._rollback()
        return (False,str(traceback.format_exc()))

def generateId():
    return int(os.urandom(4).encode('hex'),16) / 2

def register(request,username,password,email=None):
    try:
        user = User.objects.create_user(username = username, password = password, email = email)
        user.is_staff = False
        user.save()
        # create a blank lc user and associate with user object
        lcuser = LcUser(id=generateId(),user = user, time_joined = int(time()), join_ip = request.META['REMOTE_ADDR'])
        lcuser.save()
        user = auth.authenticate(username=username, password=password)
        auth.login(request, user);
        request.session['uid'] = lcuser.id
        return (True,lcuser.id)
    except:
        connection._rollback()
        return (False,str(traceback.format_exc()))

def logout(request):
    try:
        auth.logout(request)
        return (True,'')
    except:
        return (False,str(traceback.format_exc()))
