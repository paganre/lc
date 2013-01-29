from django.views.decorators.csrf import csrf_protect
from django.contrib import auth
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from webapp import user
from webapp.aleister import Aleister
import json
import traceback
import requests
from django.template.loader import get_template
from django.template import Context


# Common site request forgery protection risk
# Request is obtained from the login.html via POST
# I am using both CSRF Middleware and csrf_protect() for extra security
# More info: https://docs.djangoproject.com/en/dev/ref/contrib/csrf/
@csrf_protect
def home(request):
    return render_to_response('home.html',{"user": request.user},context_instance=RequestContext(request))

@csrf_protect
def submit(request):
    if request.user and request.user.is_authenticated:
        return render_to_response('submit.html',{"user": request.user},context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect("/")

@csrf_protect
def link(request):
    if request.user and request.user.is_authenticated:
        link = request.POST.get('link','')
        # head request to link
        if not (link.startswith('http://') or link.startswith('https://')):
            link = 'http://'+link
        try:
            r = requests.head(link)
        except:
            return HttpResponse(json.dumps({'result':0,'parsed':'unreachable, check url'}))
        
        if r.ok:
            r = requests.get(link)
            crawler = Aleister()
            crawler.feed(r.text)
            host = crawler.parse_domain(r.url)
            t = get_template('parsed_url.html')
            context = {
                'title':crawler.title,
                'domain':host
                }
            return HttpResponse(json.dumps({'result':0,'html':t.render(Context(context))}))
        else:
            return HttpResponse(json.dumps({'result':0,'parsed' : r.status_code})) 
    else:
        return HttpResponse(json.dumps({'result':-1,'parsed':'not authed'}))
    
@csrf_protect
def register(request):
    name = request.POST.get('username','')
    password = request.POST.get('password','')
    email = request.POST.get('email','')
    if name and password:
        res = user.register(request,name,password,email)
        if(res[0]):
            return HttpResponse(json.dumps({'result':0}))
        else:
            return HttpResponse(json.dumps({'result':-1,'error':'Username taken'}))
    return HttpResponse(json.dumps({'result':-1,'error':"Fields not set"}))

@csrf_protect
def login(request):
    name = request.POST.get('username','')
    password = request.POST.get('password','')
    if name and password:
        res = user.login(request,name,password)
        if(res[0]):
            return HttpResponse(json.dumps({'result':0}))
        else:
            return HttpResponse(json.dumps({'result':-1,'error':'Wrong Credentials'}))
    return HttpResponse(json.dumps({'result':-1,'error':'Fields not set'}))
        

def logoutUser(request):
    auth.logout(request)
    return HttpResponseRedirect("/")
