"""saltshaker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^svn_list', views.svn_list, name='svn_list'),
    url(r'ajax_get_json_tree',views.ajax_get_json_tree,name='svn_ajax'),
    url(r'get_projects',views.get_projects,name='get_projects'),
    url(r'branch_create',views.branch_create,name='branch_create'),
    url(r'get_branches',views.get_branches,name='get_branches'),
    url(r'branch_merge',views.branch_merge,name='branch_merge'),
]
