from django.db import models
from django import forms
from django.utils import timezone
from django.contrib.auth.models import User
import os
from uuid import uuid4

#Django provides a table called user that stores basic user information like username, password and email id.

class Pcuser(models.Model):
    #username
    user = models.OneToOneField(User)
    #location
    location = models.CharField(max_length=30)
    #first_name
    first_name = models.CharField(max_length=30)
    #last_name
    last_name = models.CharField(max_length=40)
    #phone number
    phone = models.CharField(max_length=15)
    #gender
    gender = models.CharField(max_length=1)
    #for reset_password
    reset_pass = models.CharField(default="",max_length=32)
    
    def __unicode__(self):
        return self.user.username
    
    
#Post table stores details about posts

class Post(models.Model):
    #The owner of the post
    owner = models.ForeignKey(Pcuser, null=False, related_name='owner')
    #title
    title_post = models.CharField(max_length=30)
    #description
    description_post = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.owner.user.username