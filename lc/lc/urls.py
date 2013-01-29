from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'webapp.views.home', name='home'),
    url(r'^register/$','webapp.views.register'),
    url(r'^login/$','webapp.views.login'),
    url(r'^logout/$', 'webapp.views.logoutUser'),
)



