from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'webapp.views.home', name='home'),
    url(r'^register/$','webapp.views.register'),
    url(r'^login/$','webapp.views.login'),
    url(r'^submit/$','webapp.views.submit'),
    url(r'^link/$','webapp.views.link'),
    url(r'^create/$','webapp.views.create'),
    url(r'^logout/$', 'webapp.views.logoutUser'),
    url(r'^scribe/$','webapp.views.scribe'),
    url(r'^retrieve/$','webapp.views.retrieve'),
    url(r'^t/(?P<tid>\d+)','webapp.views.thread'),
    url(r'^vote/$','webapp.views.vote'),
    url(r'^notif/$','webapp.views.notif'),
    url(r'^remnot/$','webapp.views.rem_notif'),
    url(r'^u/(?P<uid>\d+)','webapp.views.userpage'),
    url(r'^tag/$','webapp.views.tag'),
    url(r'^tag/(?P<tagid>\d+)','webapp.views.get_tag'),
    url(r'^follow/$','webapp.views.follow'),
    url(r'^unfollow/$','webapp.views.unfollow'),
    url(r'^cus/$','webapp.views.cus'),
    url(r'^rhome/$','webapp.views.home_redis'),
)



