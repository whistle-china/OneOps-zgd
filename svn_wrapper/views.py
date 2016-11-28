#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright(C) 2016
Environment:python 2.7.10
Package: Django 1.8.4
@version: v1.0
@author: RoyFu{<mailto:royfu77@sina.com>}
@license: Apache Licence 
@file: views.py
@CreateTime: 16/8/15 下午4:01
@ModifyTime: 16/8/15 下午4:01
"""


from django.conf import settings as DJ_SETTINGs
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render_to_response, render
from django.contrib.auth.decorators import login_required
import json
import os, time
import logging
from django.core import serializers
import pysvn
import xml.dom.minidom
import subprocess
import dateutil.parser

logger = logging.getLogger('django')


#######################################Crete_branche&Conflict check&merge branche###########################
TRUNK_BASE = 'svn://192.168.1.204/trunk/'
BRANCH_BASE = 'svn://192.168.1.204/branches/'
SVN_BASE = 'svn://192.168.1.204/'

LOCAL_TRUNK_BASE = '/usr/local/svn/trunk/'
tree_conflict_list = []

def callback_get_log_message():
    return True, ''

def callback_notify( event_dict ):
    global tree_conflict_list
    global LOCAL_TRUNK_BASE

    if str(event_dict['action']) == 'tree_conflict':
        tree_conflict_list.append(event_dict['path'].replace(LOCAL_TRUNK_BASE,''))
    return

@login_required(login_url="/account/login/")
def get_projects(request):
    client = pysvn.Client()

    fs = client.list(TRUNK_BASE)
    if fs is None or len(fs) == 0:
        return HttpResponse(json.dumps({'ret':1, 'msg':'no projects'}))

    projects = []
    for (f,t) in fs:
        if str(f.kind) == 'dir':
            name = f.path.split('/')[-1]
            if name == 'trunk':
                continue
            projects.append(name)

    if len(projects)  == 0:
        return HttpResponse(json.dumps({'ret':2, 'msg':'no projects'}))


    return HttpResponse(json.dumps({'ret':0, 'projects':projects}))

@login_required(login_url="/account/login/")
def get_branches(request):
    # check input valid
    pn = request.GET.get('project_name')
    if pn is None or pn.strip() == '':
        return HttpResponse(json.dumps({'ret':1, 'msg':'项目不合法'}))
    pn = pn.strip()

    # check project exit in svn
    client = pysvn.Client()
    client.callback_get_log_message = callback_get_log_message

    p_found = False
    p_path = TRUNK_BASE + pn
    try:
        fs = client.list(TRUNK_BASE)
        for (f,t) in fs:
            if str(f.kind) == 'dir' and f.path == p_path:
                p_found = True
                break
    except:
        return HttpResponse(json.dumps({'ret':999, 'msg':'系统异常，请重试！'}))

    if not p_found:
        return HttpResponse(json.dumps({'ret':2, 'msg':'svn中项目不存在'}))

    # check branch exist in svn
    bp_path = BRANCH_BASE + pn + r'/'
    is_filter = False
    branches = []
    try:
        fs = client.list(bp_path)
        for (f, t) in fs:
            if str(f.kind) == 'dir':
                bn = f.path.split('/')[-1]
                if not is_filter and  bn == pn:
                    is_filter =True
                    continue
                branches.append(bn)
    except:
        return HttpResponse(json.dumps({'ret':3, 'msg':'该项目不存在分支！'}))

    if len(branches) == 0:
        return HttpResponse(json.dumps({'ret':4, 'msg':'该项目不存在分支！'}))

    return HttpResponse(json.dumps({'ret':0, 'branches':branches}))

@login_required(login_url="/account/login/")
def branch_merge(request):
    pn = request.GET.get('project_name')
    bn = request.GET.get('branch_name')
    is_dry = int(request.GET.get('is_dry'))

    # check param valid
    if bn is None or bn.strip() == '':
        return HttpResponse(json.dumps({'ret':1, 'msg':'分支名称不合法'}))
    bn = bn.strip()

    if pn is None or pn.strip() == '':
        return HttpResponse(json.dumps({'ret':2, 'msg':'项目不合法'}))
    pn = pn.strip()

    if is_dry not in [0, 1]:
        return HttpResponse(json.dumps({'ret':3, 'msg':'is_dry不合法'}))

    # check project exist in svn
    client = pysvn.Client()
    client.callback_get_log_message = callback_get_log_message

    p_found = False
    p_path = TRUNK_BASE + pn
    try:
        fs = client.list(TRUNK_BASE)
        for (f,t) in fs:
            if str(f.kind) == 'dir' and f.path == p_path:
                p_found = True
                break
    except:
        return HttpResponse(json.dumps({'ret':998, 'msg':'项目异常'})) 

    if not p_found:
        return HttpResponse(json.dumps({'ret':4, 'msg':'svn中不存在该项目'}))

    # check branch exist in svn
    bp_son_found = False
    bp_path = BRANCH_BASE + pn + r'/'
    bp_son_path = bp_path + bn
    try:
        fs = client.list(bp_path)
        for (f,t) in fs:
            if str(f.kind) == 'dir' and f.path == bp_son_path:
                bp_son_found = True
                break
    except:
        return HttpResponse(json.dumps({'ret':997, 'msg':'分支异常'})) 

    if not bp_son_found:
        return HttpResponse(json.dumps({'ret':5, 'msg':'分支名不存在'})) 

    # do merge
    client.update(LOCAL_TRUNK_BASE)
    client.callback_notify = callback_notify
    p_local_path = LOCAL_TRUNK_BASE + pn
    
    client.merge_reintegrate(bp_son_path, pysvn.Revision(pysvn.opt_revision_kind.head), p_local_path, dry_run=True)
    global tree_conflict_list
    tree_conflicts = tree_conflict_list
    tree_conflict_list = []

    if is_dry == 1 or len(tree_conflicts) != 0:
        return HttpResponse(json.dumps({'ret':0, 'tree_conflicts':tree_conflicts}))
        
    client.merge_reintegrate(bp_son_path, pysvn.Revision(pysvn.opt_revision_kind.head), p_local_path)
    client.checkin(p_local_path, '')

    tree_conflicts = tree_conflict_list
    tree_conflict_list = []
    return HttpResponse(json.dumps({'ret':0, 'tree_conflicts':tree_conflicts}))

@login_required(login_url="/account/login/")
def branch_create(request):
    bn = request.GET.get('branch_name')
    pn = request.GET.get('project_name')

    # check param valid
    if bn is None or bn.strip() == '':
        return HttpResponse(json.dumps({'ret':1, 'msg':'分支名称不合法'}))
    bn = bn.strip()

    if pn is None or pn.strip() == '':
        return HttpResponse(json.dumps({'ret':2, 'msg':'项目不合法'}))
    pn = pn.strip()

    # check project exist in svn
    client = pysvn.Client()
    client.callback_get_log_message = callback_get_log_message

    p_found = False
    p_path = TRUNK_BASE + pn
    try:
        fs = client.list(TRUNK_BASE)
        for (f,t) in fs:
            if str(f.kind) == 'dir' and f.path == p_path:
                p_found = True
                break
    except:
        return HttpResponse(json.dumps({'ret':998, 'msg':'项目查询异常'}))

    if not p_found:
        return HttpResponse(json.dumps({'ret':3, 'msg':'svn中不存在该项目'}))

    # check branch exist in svn
    bp_son_found = False
    bp_path = BRANCH_BASE + pn + r'/'
    bp_son_path = bp_path + bn
    try:
        fs = client.list(bp_path)
        for (f,t) in fs:
            if str(f.kind) == 'dir' and f.path == bp_son_path:
                bp_son_found = True
                break 
    except:
        client.mkdir(bp_path, '');

    if bp_son_found:
        return HttpResponse(json.dumps({'ret':4, 'msg':'分支名已经存在'})) 

    try:
        client.copy(p_path, bp_son_path)
    except Exception,e:
        logger.error(e)
        return HttpResponse(json.dumps({'ret':999, 'msg':'创建分支异常'}))

    return HttpResponse(json.dumps({'ret':0}))


###################get svn_list################################
def get_svn_list(url):
    svn_add="svn://192.168.1.204"
    svn_url=svn_add+url
    svn_username="admin"
    svn_passwd="admin"
    cmd = "svn list --xml "+ svn_url + " --username " + svn_username + " --password " + svn_passwd
    handle = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    doc = xml.dom.minidom.parseString(handle.communicate()[0])
    dir_list_xml = []
    for entry_node in doc.getElementsByTagName("entry"):
        path_node = entry_node.getElementsByTagName("name")[0]
        if url =='/':
            path_name = url + path_node.childNodes[0].data
        else:
            path_name = url + '/' + path_node.childNodes[0].data

        author_node = entry_node.getElementsByTagName("author")[0]
        author = author_node.childNodes[0].data

        commit_node = entry_node.getElementsByTagName("commit")[0]
        revision = commit_node.getAttribute("revision")

        date_node = entry_node.getElementsByTagName("date")[0]
        date_info = date_node.childNodes[0].data
        year = str(dateutil.parser.parse(date_info).year)
        month = str(dateutil.parser.parse(date_info).month)
        day = str(dateutil.parser.parse(date_info).day)
        hour = str(dateutil.parser.parse(date_info).hour)
        minutes = str(dateutil.parser.parse(date_info).minute)
        second = str(dateutil.parser.parse(date_info).second)
        file_date = year + '-' + month + '-' + day + ' ' + hour + ":" + minutes + ":" + second

        if entry_node.getAttribute("kind") == "dir":
            file_type='dir'
        else:
            file_type='file'

        dir_list_xml = create_dict_tree(path_name, file_type, author, revision, file_date, dir_list_xml)

    return dir_list_xml


#############判断目录下是否为空###############
def get_sub_path(url):
    svn_add = "svn://192.168.1.204"
    svn_url = svn_add + url
    svn_username = "admin"
    svn_passwd = "admin"
    cmd = "svn list --xml " + svn_url + " --username " + svn_username + " --password " + svn_passwd
    handle = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    doc = xml.dom.minidom.parseString(handle.communicate()[0])

    if len(doc.getElementsByTagName("entry"))>0:
        return True
    else:
        return False

######################对svn list的xml结果进行字符处理###################
def create_dict_tree(line, file_type, author, revision, file_date, dir_list):
    ###切割得到一个列表

    path_url = line
    dir_str = line.split('/')

    ## 判断行是否为目录
    if file_type == "dir":
        if get_sub_path(path_url):

            dir_list.append({"title": dir_str[-1], "author": author, "revision": revision, "file_date": file_date,
                             "path_url":path_url, "folder": "true", "expanded": True, "lazy": True})
        else:
            dir_list.append({"title": dir_str[-1], "author": author, "revision": revision, "file_date": file_date,
                                 "path_url": path_url, "folder": "true", "expanded": "false", "lazy": False})

    else:
    ## 文件处理
        dir_list.append({"title": dir_str[-1], "author": author, "revision": revision, "file_date": file_date,
                             "doc": "true", "path_url":path_url, "lazy": False})

    return dir_list

#################接受前端查询request，并返回json数据给前端###############

#@login_required(login_url="/account/login/")
def ajax_get_json_tree(request):
    #根据前台发出的请求来实现按节点查询数据
    request_url = request.GET.get('path_url','')
    result_xml = get_svn_list(request_url)
    json_data = json.dumps(result_xml)
    return HttpResponse(json_data, content_type="application/json")

# SVN views .
#@login_required(login_url="/account/login/")
def svn_list(request):
    return render(request, 'svn_wrapper/svn_list.html')
