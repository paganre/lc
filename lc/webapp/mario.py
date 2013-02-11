from django.http import HttpRequest
import redis
from webapp import thread as t

def is_ajax_post(request):
    return (request.is_ajax() and request.method == 'POST')

def is_ajax_get(request):
    return (request.is_ajax() and request.method == 'GET')

def is_spam(tid):
    r = redis.Redis(db = 1)
    res = t.get_thread_header(tid)
    # We will write a function in Mario to update the spamlist
    
    #banned_thread_list = ('2118349089',)
    banned_thread_list = r.sdiff('banned_thread')
    for tidb in banned_thread_list:
        if tid == int(tidb):
            return True

    #rejected_domain_list = ('1russianbrides.com',)
    rejected_domain_list = r.sdiff('banned_domain')
    for spam in rejected_domain_list:
        if res[1]['domain'].find(spam) != -1:
            return True
    return False

def is_ip_banned(request):
    r = redis.Redis(db = 1)
    client_ip = get_client_ip(request)
    return r.exists('ipban:'+str(client_ip))

def is_username_banned(username):
    r = redis.Redis(db = 1)
    return r.exists('unameban:'+str(username))

def check_registration_ip(request):
    # User can register at most 5 accounts in 5 minutes
    r = redis.Redis(db = 1)
    client_ip = get_client_ip(request)
    if r.exists('ipreg:'+str(client_ip)):
        num = int(r.get('ipreg:'+str(client_ip)))
        if num < 5:
            r.incr('ipreg:'+str(client_ip))
            return True
        else:
            return False
    else:
        r.set('ipreg:'+str(client_ip),1)
        r.expire('ipreg:'+str(client_ip),300)
        return True


def check_ip(request):
    # At most 500 requests from the same IP in 5 minutes
    r = redis.Redis(db = 1)
    client_ip = get_client_ip(request)
    if r.exists('ipreq:'+str(client_ip)):
        num = int(r.get('ipreq:'+str(client_ip)))
        if num < 500:
            r.incr('ipreq:'+str(client_ip))
            return True
        else:
            return False
    else:
        r.set('ipreq:'+str(client_ip),1)
        r.expire('ipreq:'+str(client_ip),300)
        return True

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip