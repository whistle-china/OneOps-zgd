# -*- coding: utf-8 -*-
__author__ = 'hyddd'

from django.conf import settings as DJ_SETTINGs
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render_to_response, render
from django.contrib.auth.decorators import login_required
import json
import time
import jenkins
import logging

logger = logging.getLogger('django')

@login_required(login_url="/account/login/")
def job_list(request):
    server = jenkins.Jenkins(DJ_SETTINGs.JENKINS_URL, username=DJ_SETTINGs.JENKINS_USER, password=DJ_SETTINGs.JENKINS_PWD)
    jobs = server.get_jobs()
    credentials = server.get_credential_info()

    for job in jobs:
        info = server.get_job_info(job['name'])
        job['lastSuccessfulBuild'] = info['lastSuccessfulBuild']
        job['lastUnsuccessfulBuild'] = info['lastUnsuccessfulBuild']
        job['displayName'] = info['displayName']
        job['desc'] = info['description']

    return render(request, 'jenkins_wrapper/job_list.html', {'jobs': jobs, 'credentials': credentials})

@login_required(login_url="/account/login/")
def check_job_exist(request):
    job_name = request.GET.get('job_name')

    # check param valid
    if job_name is None or job_name.strip() == '':
        return HttpResponse('项目名称不合法')
    job_name = job_name.strip()

    try:
        # check job name exist
        server = jenkins.Jenkins(DJ_SETTINGs.JENKINS_URL, username=DJ_SETTINGs.JENKINS_USER, password=DJ_SETTINGs.JENKINS_PWD)
        jobs = server.get_jobs()
        isFound = False
        for job in jobs:
            if job['name'] == job_name:
                isFound = True
                break
        if isFound:
            return HttpResponse('项目名称已经存在')

        return HttpResponse('0')
    except:
        return HttpResponse('系统异常')


@login_required(login_url="/account/login/")
def check_is_building(request):
    job_name = request.GET.get('job_name')

    # check param valid
    if job_name is None or job_name.strip() == '':
        return HttpResponse('项目名称不合法')
    job_name = job_name.strip()

    try:
        # check job name exist
        server = jenkins.Jenkins(DJ_SETTINGs.JENKINS_URL, username=DJ_SETTINGs.JENKINS_USER, password=DJ_SETTINGs.JENKINS_PWD)
        infos = server.get_job_info(job_name)
        if infos['lastBuild'] is None:
            return HttpResponse('0')

        last_build_num = infos['lastBuild']['number']
        last_succ_build_num = -1
        last_unsucc_build_num = -1
        if infos['lastSuccessfulBuild'] is not None:
            last_succ_build_num = infos['lastSuccessfulBuild']['number']
        
        if infos['lastUnsuccessfulBuild'] is not None:
            last_unsucc_build_num = infos['lastUnsuccessfulBuild']['number']

        if last_build_num != last_succ_build_num and last_build_num != last_unsucc_build_num:
            return HttpResponse('正在构建build(#%d#)' % last_build_num)
        else:
            return HttpResponse('0')
    except:
        return HttpResponse('系统异常')

@login_required(login_url="/account/login/")
def job_create(request):
    job_name = request.GET.get('job_name')
    svn_addr = request.GET.get('svn_addr')
    job_type = request.GET.get('job_type')
    credential = request.GET.get('credential')
    root_pom = request.GET.get('root_pom')
    goals = request.GET.get('goals')

    # check param valid
    if job_name is None or job_name.strip() == '':
        return HttpResponse('项目名称不合法')
    job_name = job_name.strip()

    if svn_addr is None or svn_addr.strip() == '':
        return HttpResponse('SVN地址不合法')
    svn_addr = svn_addr.strip()

    if job_type is None or job_type.strip() == '':
        return HttpResponse('项目类型不合法')
    job_type = job_type.strip()

    if root_pom is None or root_pom.strip() == '':
        return HttpResponse('root POM不合法')
    root_pom = root_pom.strip()

    if goals is None:
        goals = ''
    else:
        goals = goals.strip()

    if credential is None or credential.strip() == '':
        return HttpResponse('验证账户不合法')
    credential = credential.strip()

    # check support job type
    supported_job_types = ['maven']
    if job_type not in supported_job_types:
        return HttpResponse('项目类型不支持')

    try:
        # check job name exist
        server = jenkins.Jenkins(DJ_SETTINGs.JENKINS_URL, username=DJ_SETTINGs.JENKINS_USER, password=DJ_SETTINGs.JENKINS_PWD)    
        jobs = server.get_jobs()
        isFound = False
        for job in jobs:
            if job['name'] == job_name:
                isFound = True
                break 
        if isFound:
            return HttpResponse('项目名称已经存在')

        # check credentail valid
        credentials = server.get_credential_info()
        isFound = False
        for c in credentials:
            if c['id'] == credential:
                isFound = True
                break
        if not isFound:
            return HttpResponse('SVN验证不合法')
    
        # create job    
        config = DJ_SETTINGs.JENKINS_MAVEN_CONFIG
        config = config.replace('{%SVN_ADDR%}', svn_addr).replace('{%CID%}', credential).replace('{%ROOT_POM%}', root_pom).replace('{%GOALS%}', goals)
        server.create_job(job_name, config)

        return HttpResponse(0)
    except:
        return HttpResponse('系统异常')



@login_required(login_url="/account/login/")
def build(request):
    job_name = request.GET.get('job_name')

    # check param valid
    if job_name is None or job_name.strip() == '':
        return HttpResponse(json.dumps({'ret':1, 'msg':'项目名称不合法'}))
    job_name = job_name.strip()
   
    try: 
        server = jenkins.Jenkins(DJ_SETTINGs.JENKINS_URL, username=DJ_SETTINGs.JENKINS_USER, password=DJ_SETTINGs.JENKINS_PWD)
        infos = server.get_job_info(job_name)
        nextBuildNumber = infos['nextBuildNumber']

        time.sleep(2)
        server.build_job(job_name)

        last_succ_build_num = -1
        last_unsucc_build_num = -1
        while True:
            time.sleep(1)

            infos = server.get_job_info(job_name)
            #if infos['lastBuild'] is None:
            #    return HttpResponse(json.dumps({'ret':0, 'succ':-1, 'unsucc':-1}))

            #last_build_num = infos['lastBuild']['number']
            if infos['lastSuccessfulBuild'] is not None:
                last_succ_build_num = infos['lastSuccessfulBuild']['number']
            else:
                last_succ_build_num = -1

            if infos['lastUnsuccessfulBuild'] is not None:
                last_unsucc_build_num = infos['lastUnsuccessfulBuild']['number']
            else:
                last_unsucc_build_num = -1

            if nextBuildNumber <= last_succ_build_num or nextBuildNumber <= last_unsucc_build_num:
                break

        return HttpResponse(json.dumps({'ret':0, 'succ':last_succ_build_num, 'unsucc':last_unsucc_build_num}))
    except Exception,e:
        logger.error(e)
        return HttpResponse(json.dumps({'ret':999, 'msg':'系统异常'}))
