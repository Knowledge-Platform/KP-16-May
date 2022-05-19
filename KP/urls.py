from django.contrib import admin
from django.urls import path, include
from django import views
from . import views
from django.shortcuts import render
from django.conf.urls.static import static
from django.conf import settings

admin.site.site_header = "Knowledge Platform Admin"
admin.site.site_title = "Knowledge Platform Admin Portal"
admin.site.index_title = "Welcome to CData Knowledge Platform"

urlpatterns = [
    path('',views.home, name='home'),
    path('contribute',views.contribute, name='contribute'),
    path('tagsgeneration',views.tagsgeneration, name='tagsgeneration'),
    path('jira',views.jira,name='jira'),
    path('salesforce', views.salesforce,name='salesforce'),
    path('salesforcedisplay', views.salesforcedisplay,name='salesforcedisplay'),
]