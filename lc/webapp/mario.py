from django.http import HttpRequest
import redis

def is_ajax_post(request):
    return (request.is_ajax() and request.method == 'POST')

def is_ajax_get(request):
    return (request.is_ajax() and request.method == 'GET')

def check_ip(request):
    r = redis.Redis()
    client_ip = get_client_ip(request)
    if r.exists('ipflw:'+str(client_ip)):
        num = r.get('ipflw:'+str(client_ip))
        if num < 500:
            r.incr('ipflw:'+str(client_ip))
            return True
        else:
            return False
    else:
            r.set('ipflw:'+str(client_ip),1)
            r.expire('ipflw:'+str(client_ip),300)
            return True

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip