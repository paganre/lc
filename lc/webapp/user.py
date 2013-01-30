from django.contrib.auth.models import User
from webapp.models import LcUser
from django.db import connection
from time import time
from django.contrib import auth
import traceback
import os

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
