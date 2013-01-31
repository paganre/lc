from django.views.decorators.csrf import csrf_protect
from django.contrib import auth
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from webapp import user
from webapp.aleister import Aleister
from webapp import thread as t
from webapp import domain as d
from webapp import comment as c
import json
import traceback
import requests
from django.template.loader import get_template
from django.template import Context
from webapp import alfred
from django.http import Http404

# Common site request forgery protection risk
# Request is obtained from the login.html via POST
# I am using both CSRF Middleware and csrf_protect() for extra security
# More info: https://docs.djangoproject.com/en/dev/ref/contrib/csrf/

@csrf_protect
def thread(request,tid):
    try:
        th = t.get_full_thread(int(tid))
        return HttpResponse(json.dumps(th))
    except:
        raise Http404

@csrf_protect
def retrieve(request):
    """
    used to retrieve html with ajax requests - with page parameters
    """
    try:
        type = request.POST.get('type','')
        if type == 'comment':
            cid = int(request.POST.get('id',''))
            out = c.get_comment(cid)
            comment = None
            if out[0]:
                comment = out[1]
            else:
                return HttpResponse(json.dumps({'result':-1,'error':out[1]}))
            context = {}
            context.update({'c':comment})
            page = request.POST.get('page','')
            context.update({'page':page})
            if page == 'home':
                has_panel = int(request.POST.get('has_panel',''))
                tid = int(request.POST.get('tid',''))
                context.update({'has_panel':has_panel})
                context.update({'tid':tid})
            t = get_template('generic/comment.html')
            html = t.render(Context(context))
            return HttpResponse(json.dumps({'result':0,'html':html}))
        else:
            return HttpResponse(json.dumps({'result':-1,'error':'unknown type'}))
    except:
        return HttpResponse(json.dumps({'result':-1,'error':str(traceback.format_exc())}))
             

@csrf_protect
def scribe(request):
    if request.user and request.user.is_authenticated() and 'uid' in request.session:
        try:
            tid = int(request.POST.get('tid',''))
            text = request.POST.get('text','')
            parent = request.POST.get('parent','')
            if parent == '':
                parent = None
            if(text.strip() == ''):
                return HttpResponse(json.dumps({'result':-1,'text':'no text'}))
            res = c.add_comment(int(request.session['uid']),tid,text,parent)
            if(res[0]):
                return HttpResponse(json.dumps({'result':0,'id':res[1]}))
            else:
                return HttpResponse(json.dumps({'result':-1,'error':res[1]}))
        except:
            return HttpResponse(json.dumps({'result':-1,'error':str(traceback.format_exc())}))
    else:
        return HttpResponse(json.dumps({'result':-1,'error':'not authed'}))

@csrf_protect
def home(request):
    tids = alfred.get_main()
    headers = [t.get_thread_header(tid) for tid in tids]
    headers = [h[1] for h in headers if h[0]]
    for h in headers:
        res = alfred.get_best_subthread(h['id'])
        if(res[0]):
            h['comments'] = res[1]
        else:
            h['comments'] = []
    return render_to_response('home.html',{"user": request.user,"headers":headers},context_instance=RequestContext(request))

@csrf_protect
def submit(request):
    if request.user and request.user.is_authenticated():
        return render_to_response('submit.html',{"user": request.user},context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect("/")

@csrf_protect
def link(request):
    if request.user and request.user.is_authenticated():
        link_ = request.POST.get('link','')
        # head request to link
        if not (link_.startswith('http://') or link_.startswith('https://')):
            link = 'http://'+link_
        else:
            link = link_
        try:
            r = requests.head(link)
        except:
            return HttpResponse(json.dumps({'result':0,'error':'unreachable, check url'}))
        if r.ok:
            r = requests.get(link)
            crawler = Aleister()
            crawler.feed(r.text)
            host = crawler.parse_domain(r.url)
            # check (title,host) here to make sure that the item was not created before 
            t = get_template('parsed_url.html')
            context = {
                'title':crawler.title,
                'domain':host,
                'url':link,
                'url_':link_
                }
            return HttpResponse(json.dumps({'result':0,'html':t.render(Context(context))}))
        else:
            return HttpResponse(json.dumps({'result':0,'error' : 'returned '+str(r.status_code)})) 
    else:
        return HttpResponse(json.dumps({'result':-1,'error':'not authed'}))

@csrf_protect
def create(request):
    if request.user and request.user.is_authenticated():
        link = request.POST.get('link','')
        title = request.POST.get('title','')
        suggested = request.POST.get('suggested','')
        domain_name = request.POST.get('domain','')
        domain_name = domain_name[1:len(domain_name)-1] # strip parantheses
        # TODO: check (suggested,domain) here again - to make sure it's unique
        res = d.createnx_domain(domain_name)
        domain = None
        # check if domain is retrieved (or created) successfully - if not rollback
        if(res[0]):
            domain = res[0]
        else:
            return HttpResponse(json.dumps({'result':-1,'error':res[1]}))
        # create thread
        res = t.create_thread(int(request.session['uid']),title,suggested,domain,link)
        if(res[0]):
            return HttpResponse(json.dumps({'result':0,'tid':str(res[1])}))
        else:
            return HttpResponse(json.dumps({'result':-1,'error':res[1]}))
    else:
        return HttpResponse(json.dumps({'result':-1,'error':'not authed'}))
    
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
            return HttpResponse(json.dumps({'result':-1,'error':res[1]}))
    return HttpResponse(json.dumps({'result':-1,'error':'Fields not set'}))
        

def logoutUser(request):
    auth.logout(request)
    return HttpResponseRedirect("/")
