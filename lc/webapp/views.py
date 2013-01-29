from django.views.decorators.csrf import csrf_protect
from django.contrib import auth
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse

# Common site request forgery protection risk
# Request is obtained from the login.html via POST
# I am using both CSRF Middleware and csrf_protect() for extra security
# More info: https://docs.djangoproject.com/en/dev/ref/contrib/csrf/
@csrf_protect
def home(request):
    loginfail = False
    if request.method == 'POST':
        isRegister = request.POST.get('isRegister', '')
        if isRegister == "True":
            rnickname = request.POST.get('rnickname','')
            rpassword = request.POST.get('rpassword','')
            remail = request.POST.get('remail','')
            if rnickname and rpassword:
                #-------- -------- -------
                #Uncomment the body of the if-clause
                #To activate registration
                #-------- -------- -------
                #user = User.objects.create_user(username = rnickname,
                #                                password = rpassword,
                #                                email = remail)
                #user.is_staff = False
                #user.save()
                #auth.login(request, user)
                return HttpResponseRedirect("")
            else:
                return HttpResponseRedirect("")
        else:
            nickname = request.POST.get('nickname', '')
            password = request.POST.get('password', '')
            user = auth.authenticate(username=nickname, password=password)
            if user is not None and user.is_active:
                auth.login(request, user);
                return HttpResponseRedirect("")
            else:
                loginfail = True
                return render_to_response('home.html',{"user": request.user, "loginfail": loginfail},context_instance=RequestContext(request))
    else:
        return render_to_response('home.html',{"user": request.user, "loginfail": loginfail},context_instance=RequestContext(request))

def logoutUser(request):
    leaving_user = request.user.username
    auth.logout(request)
    return HttpResponse("Bye %s!" % leaving_user)