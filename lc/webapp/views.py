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
from webapp import redisdb as db
from webapp.struct.subthread import Subthread

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
        return HttpResponseRedirect("/cus")
    s = request.GET.get('s', '')
    if s == 'a':
        algorithm_works = True
        tids_b = alfred.get_best_ordered_tag(tagid)
    else:
        algorithm_works = False
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
    return render_to_response('home.html',{"user": request.user,"uid":uid,"headers":headers,"tags":tags,"algorithm_works":algorithm_works},context_instance=RequestContext(request))

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

#redis
@csrf_protect
def follow(request):
    if not mario.check_ip(request):
        return HttpResponseRedirect("/cus")
    if not mario.is_ajax_post(request):
        return HttpResponseRedirect("/")
    if request.user and request.user.is_authenticated() and 'uid' in request.session:
        try:
            uid = int(request.session['uid'])
            tid = int(request.POST.get('tid',-1))
            if tid == -1:
                return HttpResponse(json.dumps({'result':-1,'error':'No such thread'}))
            db.follow_thread(uid,tid,True)
            return HttpResponse(json.dumps({'result':0}))
        except:
            return HttpResponse(json.dumps({'result':-1,'error':str(traceback.format_exc())}))
    else:
        return HttpResponse(json.dumps({'result':-1,'error':'not authed'}))

#redis
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
            if tid == -1:
                return HttpResponse(json.dumps({'result':-1,'error':'No such thread'}))
            db.follow_thread(uid,tid,False)
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


#redis
@csrf_protect
def vote(request):
    if not mario.check_ip(request):
        HttpResponseRedirect("/cus")
    if not mario.is_ajax_post(request):
        return HttpResponseRedirect("/")
    if request.user and request.user.is_authenticated() and 'uid' in request.session:
        try:
            cid = int(request.POST.get('cid',-1))
            vote = int(request.POST.get('vote',0))
            if cid == -1:
                return HttpResponse(json.dumps({'result':-1,'error':'No such comment'}))
            db.vote(int(request.session['uid']),cid,vote)
            return HttpResponse(json.dumps({'result':0}))
        except:
            return HttpResponse(json.dumps({'result':-1,'error':str(traceback.format_exc())}))
    else:
        return HttpResponse(json.dumps({'result':-1,'error':'not authed'}))


# redis
@csrf_protect
def thread(request,tid):
    if not mario.check_ip(request):
        return HttpResponseRedirect("/cus")
    try:
        header = db.get_thread_headers([int(tid)])[0]
        if header == None:
            raise Http404
        # TODO: temp dict fix
        if 'uid' in request.session:
            header['following'] = db.is_following(int(request.session['uid']),[int(tid)])[0]
        else:
            header['following'] = False
        header['time'] = pretty_time(int(header['time']))
        header['creator_name'] = header['cname']
        header['creator_id'] = header['cid']

        cids = db.get_thread_comments(int(tid))
        cids.reverse()
        comments = db.get_comments(cids)
        votes = [0]*len(cids)
        if 'uid' in request.session:
            uid = int(request.session['uid'])
            votes = db.did_vote(uid,cids)

        # create subthread trees
        subs = []
        for ind,c in enumerate(comments):
            # TODO: temp dict fix
            c['creator_name'] = c['cname']
            c['creator_id'] = c['cid']
            c['net_vote'] = c['up'] - c['down']
            c['id'] = cids[ind]
            c['time'] = pretty_time(c['time'])

            if c['pid'] == -1:
                subs.append(Subthread(c,[]))
            else:
                for s in subs:
                    if s.insertChildTo(c['pid'],Subthread(c,[])):
                        break
        # convert subthread trees to lists
        comment_threads = []
        for s in subs:
            comment_threads.append(s.toList(0,[]))
        
        rcomments = []
        for subthread in comment_threads:
            sub = []
            for i,c_ in enumerate(subthread):
                comment = c_[0]
                if 'uid' in request.session:
                    ind = cids.index(comment['id'])
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
            rcomments.append(sub)

        highlight = None
        #n = request.GET.get('not', '')
        #if n != '' and 'uid' in request.session:
        #    u.del_notif(int(request.session['uid']),int(n))
        #    highlight = int(n)

        #t.increment_view_count(int(tid))
        return render_to_response('thread.html',{"user": request.user,"uid":uid,"header":header,"threads":rcomments,"tid":tid,"highlight":highlight},context_instance=RequestContext(request))
    except:
        return HttpResponse(str(traceback.format_exc()))

#redis
@csrf_protect
def userpage(request,uid):
    if not mario.check_ip(request):
        HttpResponseRedirect("/cus")

    cids = db.get_user_comments(int(uid))[:15]
    comments = db.get_comments(cids)
    #TODO: temp fix for dict fields for comments / thread headers
    for ind,comment in enumerate(comments):
        comment['creator_name'] = comment['cname']
        comment['creator_id'] = comment['cid']
        comment['net_vote'] = comment['up'] - comment['down']
        comment['id'] = cids[ind]
        comment['time'] = pretty_time(comment['time'])

    tids = [int(c['tid']) for c in comments]
    tset = []
    cset = []
    headers = []
    for ind,tid in enumerate(tids):
        if tid in tset:
            tind = tset.index(tid)
            cset[tind].append(comments[ind])
        else:
            tset.append(tid)
            cset.append([comments[ind]])
            headers.append(db.get_thread_headers([tid])[0])

    # tset - unique list of threads
    # cset = [[comments]] : comment list for each thread
    username = db.swap_user_info(int(uid))
    for ind,header in enumerate(headers):
        header['comments'] = cset[ind]
        if 'uid' in request.session:
            header['following'] = db.is_following(int(request.session['uid']),[int(tset[ind])])[0]
        else:
            header['following'] = False
        header['time'] = pretty_time(int(header['time']))
        header['creator_name'] = header['cname']
        header['creator_id'] = header['cid']
    return render_to_response('userpage.html',{"username":username,"user": request.user,"headers":headers},context_instance=RequestContext(request))
    

# changed to redis
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
            comment = db.get_comments([cid])[0]
            if comment == None:
                return HttpResponse(json.dumps({'result':-1,'error':'No such comment'}))
            
            #TODO: temp fix for dict keys matching
            comment['creator_name'] = comment['cname']
            comment['creator_id'] = comment['cid']
            comment['net_vote'] = comment['up'] - comment['down']
            comment['id'] = cid
            comment['time'] = pretty_time(comment['time'])

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
             
# changed to redis
@csrf_protect
def scribe(request):
    if not mario.check_ip(request):
        return HttpResponseRedirect("/cus")
    if not mario.is_ajax_post(request):
        return HttpResponseRedirect("/")
    if request.user and request.user.is_authenticated() and 'uid' in request.session:
        try:
            tid = int(request.POST.get('tid',''))
            text = request.POST.get('text','')
            parent = int(request.POST.get('parent',-1))
            if(text.strip() == ''):
                return HttpResponse(json.dumps({'result':-1,'text':'no text'}))
            res = db.add_comment(tid,int(request.session['uid']),text,parent = parent) 
            if(res[0]):
                return HttpResponse(json.dumps({'result':0,'id':res[1]}))
            else:
                return HttpResponse(json.dumps({'result':-1,'error':res[1]}))
        except:
            return HttpResponse(json.dumps({'result':-1,'error':str(traceback.format_exc())}))
    else:
        return HttpResponse(json.dumps({'result':-1,'error':'not authed'}))

# redis temp home
@csrf_protect
def home_redis(request):
    tids = db.get_thread_ids()
    headers = db.get_thread_headers(tids)
    uid = -1
    if 'uid' in request.session:
        uid = int(request.session['uid'])
    following = db.is_following(uid,tids)
    for ind,h in enumerate(headers):
        h['comments'] = []
        h['following'] = following[ind]
        h['time'] = pretty_time(int(h['time']))
        h['creator_name'] = h['cname']
        h['creator_id'] = h['cid']
        
    return render_to_response('home.html',{"user": request.user,"uid":uid,"headers":headers,"tags":[],"algorithm_works":False},context_instance=RequestContext(request))



@csrf_protect
def home(request):
    return HttpResponse('Alp biseyler yapiyo bi saniye pampa')
    if not mario.check_ip(request):
        return HttpResponseRedirect("/cus")
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
        return HttpResponseRedirect("/cus")
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
            return HttpResponse(json.dumps({'result':0,'error':'check url'}))
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
    if 'uid' in request.session and request.user and request.user.is_authenticated():
        link = request.POST.get('link','')
        title = request.POST.get('title','')
        summary = request.POST.get('summary','')
        if summary == '':
            summary = None
        suggested = request.POST.get('suggested','')
        domain_name = request.POST.get('domain','')
        # check if not unique
        uid = int(request.session['uid'])
        tid = -1
        try:
            tid = db.create_thread(uid,title,summary,link,domain_name)
        except:
            return HttpResponse(json.dumps({'result':-1,'error':str(traceback.format_exc())}))
        return HttpResponse(json.dumps({'result':0,'tid':tid}))
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
    if (mario.is_username_banned(name) or mario.is_ip_banned(request)):
        # Do something better here ...
        return HttpResponseRedirect("/")
    if name and password:
        res = u.register(request,name,password,email)
        if(res[0]):
            if not mario.check_registration_ip(request):
                return HttpResponse(json.dumps({'result':-1,'error':'Cok fazla hesap actin! Biraz bekle...'}))
            else:
                return HttpResponse(json.dumps({'result':0}))
        else:
            return HttpResponse(json.dumps({'result':-1,'error':'Nick alinmis'}))
    return HttpResponse(json.dumps({'result':-1,'error':'Kutular bos'}))

@csrf_protect
def login(request):
    if not mario.check_ip(request):
        HttpResponseRedirect("/cus")
    if not mario.is_ajax_post(request):
        return HttpResponseRedirect("/")
    name = request.POST.get('username','')
    password = request.POST.get('password','')
    if (mario.is_username_banned(name) or mario.is_ip_banned(request)):
        # Do something better here ...
        return HttpResponseRedirect("/")
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
