from django.db import models
from django.contrib.auth.models import User

class LcUser(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.OneToOneField(User,verbose_name="related user")
    time_joined = models.IntegerField()
    join_ip = models.CharField(max_length=15)
    karma = models.IntegerField(default=0)
    status = models.IntegerField(default=0)

class Domain(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length = 250)
    logo = models.CharField(max_length = 1000)

class Thread(models.Model):
    id = models.IntegerField(primary_key=True)
    creator = models.ForeignKey('LcUser',verbose_name="creator")
    title = models.CharField(max_length = 250)
    url = models.CharField(max_length = 1000)
    domain = models.ForeignKey('Domain',verbose_name="domain")
    time_created = models.IntegerField()
    up = models.IntegerField(default=0)
    down = models.IntegerField(default=0)
    reports = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    share_views = models.IntegerField(default=0)

class Comment(models.Model):
    id = models.IntegerField(primary_key = True)
    creator = models.ForeignKey('LcUser', verbose_name="creator")
    thread = models.ForeignKey('Thread',verbose_name="thread")
    parent = models.ForeignKey('Comment',verbose_name="parent comment",default=None)
    text = models.CharField(max_length = 10000)
    time_created = models.IntegerField()
    up = models.IntegerField(default=0)
    down =models.IntegerField(default=0)
    reports = models.IntegerField(default=0)

class Tag(models.Model):
    id = models.IntegerField(primary_key = True)
    name = models.CharField(max_length = 50)
    threads = models.ManyToManyField(Thread,verbose_name="related threads")
