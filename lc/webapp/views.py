from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.middleware.csrf import get_token
from django.contrib import auth
from django.db import connection
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User
from webapp.models import LcUser,Comment,Thread
from django.http import HttpResponseRedirect, HttpResponse
from webapp.aleister import Aleister
from webapp import thread as t
from webapp import domain as d
from webapp import comment as c
from webapp import user as u
from webapp import tagger
from webapp import mario
import json
import traceback
import requests
from django.template.loader import get_template
from django.template import Context
from webapp import alfred
from django.http import Http404
from webapp.pretty_time import pretty_time

# Common site request forgery protection risk
# Request is obtained from the login.html via POST
# I am using both CSRF Middleware and csrf_protect() for extra security
# More info: https://docs.djangoproject.com/en/dev/ref/contrib/csrf/

@csrf_protect
def cus(request):
    return render_to_response('cus.html')

@csrf_protect
def get_tag(request,tagid):
    if not mario.check_ip(request):
        HttpResponseRedirect("/cus")
    tids_b = alfred.get_time_ordered_tag(tagid)
    tids = []
    for tid in tids_b:
        if not mario.is_spam(tid):
            tids = tids + [tid]
    headers = [t.get_thread_header(tid) for tid in tids]
    headers = [h[1] for h in headers if h[0]]
    
    uid = -1
    if 'uid' in request.session:
        uid = int(request.session['uid'])

    for h in headers:
        res = alfred.get_best_subthread(h['id'])
        if(res[0]):
            h['comments'] = res[1]
        else:
            h['comments'] = []
        if uid != -1:
            h['following'] = u.is_following(uid,h['id'])
        else:
            h['following'] = 0
    
    tags = tagger.get_top_tags(5)
    uid = -1
    if 'uid' in request.session:
        uid = int(request.session['uid'])
    return render_to_response('home.html',{"user": request.user,"uid":uid,"headers":headers,"tags":tags},context_instance=RequestContext(request))

@csrf_protect
def tag(request):
    if not mario.check_ip(request):
        HttpResponseRedirect("/cus")
    if not mario.is_ajax_post(request):
        return HttpResponseRedirect("/")
    if request.user and request.user.is_authenticated() and 'uid' in request.session:
        try:
            tag = request.POST.get('tag','')
            tid = int(request.POST.get('tid',0))
            if tid == 0 or tag == '':
                return HttpResponse(json.dumps({'result':-1,'error':'field not set'}))
            res = tagger.tag(int(request.session['uid']),tid,tag)
            if (res[0]):
                return HttpResponse(json.dumps({'result':0}))
            else:
                return HttpResponse(json.dumps({'result':-1,'error':res[1]}))
        except:
            return HttpResponse(json.dumps({'result':-1,'error':str(traceback.format_exc())}))
    else:
        return HttpResponse(json.dumps({'result':-1,'error':'not authed'}))

@csrf_protect
def follow(request):
    if not mario.check_ip(request):
        HttpResponseRedirect("/cus")
    if not mario.is_ajax_post(request):
        return HttpResponseRedirect("/")
    if request.user and request.user.is_authenticated() and 'uid' in request.session:
        try:
            uid = int(request.session['uid'])
            tid = int(request.POST.get('tid',-1))
            if u.follow_thread(uid,tid):
                return HttpResponse(json.dumps({'result':0}))
            else:
                return HttpResponse(json.dumps({'result':-1,'error':'user returned false'}))
        except:
            return HttpResponse(json.dumps({'result':-1,'error':str(traceback.format_exc())}))
    else:
        return HttpResponse(json.dumps({'result':-1,'error':'not authed'}))

@csrf_protect
def unfollow(request):
    if not mario.check_ip(request):
        HttpResponseRedirect("/cus")
    if not mario.is_ajax_post(request):
        return HttpResponseRedirect("/")
    if request.user and request.user.is_authenticated() and 'uid' in request.session:
        try:
            uid = int(request.session['uid'])
            tid = int(request.POST.get('tid',-1))
            u.unfollow_thread(uid,tid)
            return HttpResponse(json.dumps({'result':0}))
        except:
            return HttpResponse(json.dumps({'result':-1,'error':str(traceback.format_exc())}))
    else:
        return HttpResponse(json.dumps({'result':-1,'error':'not authed'}))

@csrf_protect
def rem_notif(request):
    if not mario.check_ip(request):
        HttpResponseRedirect("/cus")
    if not mario.is_ajax_post(request):
        return HttpResponseRedirect("/")
    if request.user and request.user.is_authenticated() and 'uid' in request.session:
        try:
            uid = int(request.session['uid'])
            cid = int(request.POST.get('cid',''))
            u.del_notif(uid,cid)
            return HttpResponse(json.dumps({'result':0}))
        except:
            return HttpResponse(json.dumps({'result':-1,'error':str(traceback.format_exc())}))
    else:
        return HttpResponse(json.dumps({'result':-1,'error':'not authed'}))

def notif(request):
    if not mario.check_ip(request):
        HttpResponseRedirect("/cus")
    if not mario.is_ajax_get(request):
        return HttpResponseRedirect("/")
    if request.user and request.user.is_authenticated() and 'uid' in request.session:
        try:
            notifs = u.get_notifs(int(request.session['uid']))
            t = get_template("notif_item.html");
            html = ""
            for n in notifs:
                cid = int(n[0])
                reply = 1
                if int(n[1]) == 0:
                    reply = 0
                c = Comment.objects.get(pk = cid)
                context = {"creator":c.creator.user.username,
                           "tid":c.thread.id,
                           "title":c.thread.title,
                           "cid":c.id,
                           "reply":reply}
                html += t.render(Context(context))
            return HttpResponse(json.dumps({'result':0,'html':html}))
        except:
            return HttpResponse(json.dumps({'result':-1,'error':str(traceback.format_exc())}))
    else:
        return HttpResponse(json.dumps({'result':-1,'error':'not authed'}))


@csrf_protect
def vote(request):
    if not mario.check_ip(request):
        HttpResponseRedirect("/cus")
    if not mario.is_ajax_post(request):
        return HttpResponseRedirect("/")
    if request.user and request.user.is_authenticated() and 'uid' in request.session:
        try:
            cid = int(request.POST.get('cid',''))
            vote = int(request.POST.get('vote',''))
            out = u.vote(int(request.session['uid']),cid,vote)
            if not out[0]:
                return HttpResponse(json.dumps({'result':-1,'error':out[1]}))
            return HttpResponse(json.dumps({'result':0}))
        except:
            return HttpResponse(json.dumps({'result':-1,'error':str(traceback.format_exc())}))
    else:
        return HttpResponse(json.dumps({'result':-1,'error':'not authed'}))


@csrf_protect
def thread(request,tid):
    if not mario.check_ip(request):
        HttpResponseRedirect("/cus")
    try:
        th = t.get_full_thread(int(tid))
        if(th[0]):
            # adjust </div> ranges
            comments = []
            votes = [0] * len(th[3])
            uid = -1
            if 'uid' in request.session:
                uid = int(request.session['uid'])
                res = u.did_vote(uid,th[3])
                if res[0]:
                    votes = res[1]
                    
            for subthread in th[2]:
                sub = []
                for i,c_ in enumerate(subthread):
                    comment = c.comment_to_dict(c_[0])
                    if 'uid' in request.session:
                        ind = th[3].index(c_[0].id)
                        if votes[ind] == 1:
                            comment.update({'up':'up-voted'})
                        elif votes[ind] == -1:
                            comment.update({'down':'down-voted'})
                    current_level = c_[1]
                    if i == len(subthread)-1:
                        sub.append([comment,range(current_level+1)])
                    else:
                        next_level = subthread[i+1][1]
                        sub.append([comment,range(current_level - next_level +1)])
                comments.append(sub)
            
            highlight = None
            n = request.GET.get('not', '')
            if n != '' and 'uid' in request.session:
                u.del_notif(int(request.session['uid']),int(n))
                highlight = int(n)
                
            t.increment_view_count(int(tid))
            return render_to_response('thread.html',{"user": request.user,"uid":uid,"header":th[1],"threads":comments,"tid":tid,"highlight":highlight},context_instance=RequestContext(request))
        else:
            return HttpResponse(th[1])
    except:
        return HttpResponse(str(traceback.format_exc())+"th[2] is :"+str(th[2])+"\r\n\ i was:"+str(i))

@csrf_protect
def userpage(request,username):
    if not mario.check_ip(request):
        HttpResponseRedirect("/cus")
    #if request.user.username==username and request.user.is_authenticated() and 'uid' in request.session:
    res = u.get_commented_threads(u.get_user_id(username))
    if res[0]:
        headers = []
        for r in res[1]:
            header = t.get_thread_header(r[0])
            if header[0]:
                sub = []
                for cid in r[1]:
                    try:
                        sub.append(Comment.objects.get(pk = int(cid)))
                    except:
                        connection._rollback()
                    header[1]['comments'] = c.get_comment_fields(sub)
                headers = headers + [header[1]]
        return render_to_response('userpage.html',{"username":username,"user": request.user,"headers":headers},context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect("/")

@csrf_protect
def retrieve(request):
    """
    used to retrieve html with ajax requests - with page parameters
    """
    if not mario.check_ip(request):
        HttpResponseRedirect("/cus")
    if not mario.is_ajax_post(request):
        return HttpResponseRedirect("/")
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
            tid = int(request.POST.get('tid',''))
            context.update({'tid':tid})
            if page == 'home':
                has_panel = int(request.POST.get('has_panel',''))
                context.update({'has_panel':has_panel})
            elif page == 'thread':
                new = int(request.POST.get('new',''))
                context.update({'new':new})
            t = get_template('generic/comment.html')
            html = t.render(Context(context))
            return HttpResponse(json.dumps({'result':0,'html':html}))
        else:
            return HttpResponse(json.dumps({'result':-1,'error':'unknown type'}))
    except:
        return HttpResponse(json.dumps({'result':-1,'error':str(traceback.format_exc())}))
             

@csrf_protect
def scribe(request):
    if not mario.check_ip(request):
        HttpResponseRedirect("/cus")
    if not mario.is_ajax_post(request):
        return HttpResponseRedirect("/")
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
    if not mario.check_ip(request):
        HttpResponseRedirect("/cus")
    s = request.GET.get('s','')
    if s == 'a':
        algorithm_works = True
        tids_b = alfred.get_best()
    else:
        algorithm_works = False
        tids_b = alfred.get_time_ordered()
    
    uid = -1
    if 'uid' in request.session:
        uid = int(request.session['uid'])

    tids = []
    for tid in tids_b:
        if not mario.is_spam(tid):
            tids = tids + [tid]

    headers = [t.get_thread_header(tid) for tid in tids]
    headers = [h[1] for h in headers if h[0]]
    for h in headers:
        res = alfred.get_best_subthread(h['id'])
        if(res[0]):
            h['comments'] = res[1]
        else:
            h['comments'] = []
        if uid != -1:
            h['following'] = u.is_following(uid,int(h['id']))
    
    tags = tagger.get_top_tags(5)
    
    return render_to_response('home.html',{"user": request.user,"uid":uid,"headers":headers,"tags":tags,"algorithm_works":algorithm_works},context_instance=RequestContext(request))

@csrf_protect
def submit(request):
    if not mario.check_ip(request):
        HttpResponseRedirect("/cus")
    if request.user and request.user.is_authenticated():
        return render_to_response('submit.html',{"user": request.user},context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect("/")

@csrf_protect
def link(request):
    if not mario.check_ip(request):
        HttpResponseRedirect("/cus")
    if not mario.is_ajax_post(request):
        return HttpResponseRedirect("/")
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
    if not mario.check_ip(request):
        HttpResponseRedirect("/cus")
    if not mario.is_ajax_post(request):
        return HttpResponseRedirect("/")
    if request.user and request.user.is_authenticated():
        link = request.POST.get('link','')
        title = request.POST.get('title','')
        summary = request.POST.get('summary','')
        if summary == '':
            summary = None
        suggested = request.POST.get('suggested','')
        domain_name = request.POST.get('domain','')
        domain_name = domain_name[1:len(domain_name)-1] # strip parantheses
        res = d.createnx_domain(domain_name)
        domain = None
        # check if domain is retrieved (or created) successfully - if not rollback
        if(res[0]):
            domain = res[0]
        else:
            return HttpResponse(json.dumps({'result':-1,'error':res[1]}))
        # check if a thread with same domain and suggested title already exists
        ds_res = t.check_domain_stitle(suggested, domain)
        if(ds_res[0]==0):
            # create thread
            res = t.create_thread(int(request.session['uid']),title,summary,suggested,domain,link)
            if(res[0]):
                return HttpResponse(json.dumps({'result':0,'tid':str(res[1])}))
            else:
                return HttpResponse(json.dumps({'result':-1,'error':res[1]}))
        else:
            if(ds_res[0]==1):
                # A thread with same domain name and suggested title exists
                msg = 'Haber sitede. Thread id: '+str(ds_res[1])
                return HttpResponse(json.dumps({'result':-1,'error':msg}))
            else:
                return HttpResponse(json.dumps({'result':-1,'error':'DB error'}))
    else:
        return HttpResponse(json.dumps({'result':-1,'error':'not authed'}))

@csrf_protect
def register(request):
    if not mario.check_ip(request):
        HttpResponseRedirect("/cus")
    if not mario.is_ajax_post(request):
        return HttpResponseRedirect("/")
    name = request.POST.get('username','')
    password = request.POST.get('password','')
    email = request.POST.get('email','')
    if name and password:
        res = u.register(request,name,password,email)
        if(res[0]):
            return HttpResponse(json.dumps({'result':0}))
        else:
            return HttpResponse(json.dumps({'result':-1,'error':'Username taken'}))
    return HttpResponse(json.dumps({'result':-1,'error':'Fields not set'}))

@csrf_protect
def login(request):
    if not mario.check_ip(request):
        HttpResponseRedirect("/cus")
    if not mario.is_ajax_post(request):
        return HttpResponseRedirect("/")
    name = request.POST.get('username','')
    password = request.POST.get('password','')
    if name and password:
        res = u.login(request,name,password)
        if(res[0]):
            return HttpResponse(json.dumps({'result':0}))
        else:
            return HttpResponse(json.dumps({'result':-1,'error':res[1]}))
    return HttpResponse(json.dumps({'result':-1,'error':'Fields not set'}))
        

def logoutUser(request):
    if not mario.check_ip(request):
        HttpResponseRedirect("/cus")
    auth.logout(request)
    return HttpResponseRedirect("/")
