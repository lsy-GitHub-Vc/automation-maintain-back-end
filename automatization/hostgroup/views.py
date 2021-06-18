#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#@time:
#@Author:lsy
#@file:
#@function:-----------

from .models import HostInfoManage,UserManage
from django.http import HttpResponse
from io import StringIO
from automatization.settings import logger
from threading import Thread
from django.core.paginator import PageNotAnInteger,Paginator,EmptyPage
import numpy as np
import copy
import paramiko
import socket
import json
import os
import xlrd

# 定义一个的线程
def Tr_async(fun):
    def wrapper(*args,**kwargs):
        thr = Thread(target=fun,args=args,kwargs=kwargs)
        thr.start()
    return wrapper



def Ins_HostInfo(request):
    try:
        logger.info('<---调用主机添加接口--->')
        body = json.loads(request.body.decode())
        logger.info('<---接收的参数:{0}--->'.format(body))

        hostname = body.get('hostname','')
        hostgroup = body.get('hostgroup','')
        hostip = body.get('hostip','')
        port = body.get('port',0)
        credential = body.get('credential','')
        description = body.get('description','')



        hostinfomanage = HostInfoManage()
        hostinfomanage.hostname = hostname
        hostinfomanage.hostgroup = hostgroup
        hostinfomanage.hostip = hostip
        hostinfomanage.port = port
        hostinfomanage.credential = credential
        hostinfomanage.description = description
        # hostinfomanage.hoststatus = hoststatus
        hostinfomanage.save()

        logger.info('<---主机信息添加成功--->'.format(body))
        data = {'code':1,'msg':'主机信息添加成功','data':'success'}
        return HttpResponse(json.dumps(data),content_type='application/json')
    except Exception as e:
        logger.info("<---异常信息:{0}  发生异常的行数:{1}--->".format(e.__traceback__.tb_lineno))
        data = {'code':2,'msg':"<---异常信息:{0}  发生异常的行数:{1}--->".format(e.__traceback__.tb_lineno),'data':'Failure'}
        return HttpResponse(json.dumps(data),content_type='application/json')

#批量插入
def Bulk_Create_HostInfo(request):
    try:
        logger.info('<---调用批量插入主机信息接口--->')
        body = json.loads(request.body.decode())
        logger.info('<---接收的参数:{0}--->'.format(body))

        filepath = body.get('filepath','')
        sheet_host_list = Execl(filepath)
        #存储插入主机表的存储
        bulk_create_host_list = []
        #存储插入主机用户表的存储
        bulk_create_user_list = []
        #存储ip和端口 为后续连通性测试准备
        clint_host_list = []
        clint_host_dict = {}
        for sheet_value_list in sheet_host_list:
            #存ip和端口
            clint_host_dict["hostip"] = sheet_value_list[2]
            clint_host_dict["port"] = sheet_value_list[3]
            clint_host_dict["credential"] = sheet_value_list[4]
            #插入主机对象
            bulk_create_host_value = HostInfoManage(hostname=sheet_value_list[0],hostgroup=str(sheet_value_list[1]),hostip=sheet_value_list[2],
                                                    port=sheet_value_list[3],credential=str(sheet_value_list[4]),description=sheet_value_list[11])
            bulk_create_host_list.append(bulk_create_host_value)

            #插入主机用户对象
            bulk_create_user_value = UserManage(name=str(sheet_value_list[4]),username=sheet_value_list[5],password=sheet_value_list[6],become_method=sheet_value_list[7],
                                                become_user=sheet_value_list[8],become_password=sheet_value_list[9],public_key=sheet_value_list[10])
            bulk_create_user_list.append(bulk_create_user_value)

            clint_host_list.append(clint_host_dict)
        #批量插入主机管理
        logger.info('<---插入主机管理表 笔数:{0}--->'.format(len(bulk_create_host_list)))
        HostInfoManage.objects.bulk_create(bulk_create_host_list)

        logger.info('<---插入主机用户管理表 笔数:{0}--->'.format(len(bulk_create_user_list)))
        UserManage.objects.bulk_create(bulk_create_user_list)
        #后续进行连通性测试(异步)
        logger.info('<---接入主机连通性测试接口 (异步)--->')
        Clint_Host_Test(clint_host_list)

        data = {'code':1,'msg':'批量数据插入完成','data':'success'}
        return HttpResponse(json.dumps(data),content_type='application/json')
    except Exception as e:
        logger.info("<---异常信息:{0}  发生异常的行数:{1}--->".format(e.__traceback__.tb_lineno))
        data = {'code':2,'msg':"<---异常信息:{0}  发生异常的行数:{1}--->".format(e.__traceback__.tb_lineno),'data':'Failure'}
        return HttpResponse(json.dumps(data),content_type='application/json')

def Execl(filepath):
    try:
        logger.info('<---调用读取execl文件接口>')
        #判断文件是否存在
        if os.path.isfile(filepath):
            #打开文件
            logger.info('<---打开文件--->')
            book = xlrd.open_workbook(filepath)
            sheet_host_list = []
            #获取页列表
            page_sheet = book.sheet_names()
            logger.info('<---获取所有页列表:{0}--->'.format(page_sheet))
            #所有页
            for sheet in page_sheet:
                #读取某一页
                sheet_dt = book.sheet_by_name(sheet)
                #行数
                rows = sheet_dt.nrows-1
                cols = sheet_dt.ncols
                im_data = np.zeros((rows,cols))
                logger.info('<---页名:{0} 数据行数:{1}--->'.format(sheet,rows))
                if rows > 0:
                    #从第二行开始读 跳过说明行
                    for i in range(rows):
                        sheet_host_data = sheet_dt.row_values(i+1)
                        sheet_host_list.append([a if isinstance(a,float)==False else int(a) for a in sheet_host_data ])
                    # for curr_row in range(1,rows):
                    #     for curr_col in range(cols):
                    #         raw_value = sheet_dt.cell(curr_row,curr_col).value
                    #     if isinstance(raw_value,)
                    return sheet_host_list
                else:
                    logger.info('路径文件:{} 无数据'.format(filepath))
                    data = {'code':2,'msg':'路径文件:{} 无数据'.format(filepath),'data':'Failure'}
                    return HttpResponse(json.dumps(data),content_type='application/json')
        else:
            logger.info('路径文件:{} 没有找到文件'.format(filepath))
            data = {'code':2,'msg':'路径文件:{} 没有找到文件'.format(filepath),'data':'Failure'}
            return HttpResponse(json.dumps(data),content_type='application/json')
    except Exception as e:
        logger.info("<---异常信息:{0}  发生异常的行数:{1}--->".format(e.__traceback__.tb_lineno))
        data = {'code':2,'msg':"<---异常信息:{0}  发生异常的行数:{1}--->".format(e.__traceback__.tb_lineno),'data':'Failure'}
        return HttpResponse(json.dumps(data),content_type='application/json')



#连通性检测
@Tr_async
def Clint_Host_Test(sheet_host_list):
    try:
        #sheet_host_list [{'hostip':'','port':22},{hostip':'','port':21}...]
        logger.info('<---目标主机连通性测试--->')
        #连通性测试
        clint_host_fai = []
        sheet_host_list_deep = copy.deepcopy(sheet_host_list)
        for host_info in sheet_host_list:
            sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            sk.settimeout(1.5)
            try:
                sk.connect((host_info['hostip'],int(host_info['port'])))
                logger.info('<---目标主机连接成功 ip:{0} 端口:{}--->'.format(host_info['hostip'],host_info['port']))
            except Exception as e:
                sheet_host_list_deep.remove(host_info)
                clint_host_fai.append(host_info)
    except Exception as e:
        logger.info("<---异常信息:{0}  发生异常的行数:{1}--->".format(e.__traceback__.tb_lineno))
    else:
        logger.info('<---连接失败的数据:{0}--->'.format(clint_host_fai))
        if clint_host_fai:
            for clint_host_fai_upd in clint_host_fai:
                HostInfoManage.objects.filter(hostip=clint_host_fai_upd['hostip'],port=clint_host_fai_upd['port'])
        logger.info('<---需要ssh连通性测试的数据:{0}--->'.format(sheet_host_list_deep))
        # if sheet_host_list_deep:
        #     Clint_SSH_Test(sheet_host_list_deep)
    finally:
        if sk:
            sk.close()


#ssh连接测试
def Clint_SSH_Test(sheet_host_list_deep):
    try:
        for ssh_host_clint in sheet_host_list_deep:
            private_key = paramiko.RSAKey.from_private_key_file(ssh_host_clint['credential'])
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    except Exception as e:
        logger.info("<---异常信息:{0}  发生异常的行数:{1}--->".format(e.__traceback__.tb_lineno))



    except Exception as e:
        pass


#查询主机信息
def Sel_HostInfo(request):
    try:
        logger.info('<---调用查询主机信息接口  获取参数:{0}>'.format(request.GET))
        #获取页码
        page = request.GET.get('page',1)
        pagesize = int(request.GET.get('pagesize',15))
        hostname = request.GET.get('hostname','')
        hostip = request.GET.get('hostip','')
        result_list = []

        if hostname:
            sel_influence_result = HostInfoManage.objects.filter(hostname=hostname)
            if sel_influence_result.exists():
                result = Data_Pagination(page,pagesize,sel_influence_result)
            else:
                logger.info('<---没有找到主机名hostname:{0} 对应的数据-->'.format(hostname))
                data = {'code':2,'msg':'没有找到主机名hostname:{0} 对应的数据'.format(hostname),'data':'Failure'}
                return HttpResponse(json.dumps(data),content_type='application/json')
        elif hostip:
            sel_influence_result = HostInfoManage.objects.filter(hostip=hostip)
            if sel_influence_result.exists():
                result = Data_Pagination(page,pagesize,sel_influence_result)
            else:
                logger.info('<---没有找到主机地址hostaddress:{0} 对应的数据--->'.format(hostip))
                data = {'code':2,'msg':'没有找到主机地址hostaddress:{0} 对应的数据'.format(hostip),'data':'Failure'}
                return HttpResponse(json.dumps(data),content_type='application/json')
        else:
            sel_influence_result = HostInfoManage.objects.all()
            if sel_influence_result.exists():
                result = Data_Pagination(page,pagesize,sel_influence_result)
            else:
                logger.info('<---没有找到数据信息--->')
                data = {'code':2,'msg':'没有找到数据信息','data':'Failure'}
                return HttpResponse(json.dumps(data),content_type='application/json')

        # logger.info('<---返回的分页数据:{}--->'.format(result))
        if result[0]:
            for result_sing in result[0]:
                result_list.append({'id':result_sing.id,'hostname':result_sing.hostname,'hostgroup':result_sing.hostgroup,'hostip':result_sing.hostip,
                                    'port':result_sing.port,'credential':result_sing.credential,'description':result_sing.description,'hoststatus':result_sing.hoststatus})
            data = {'code':1,'msg':'数据查询完成','total':result[1],'data':result_list}
        else:
            data = {'code':2,'msg':'已达最大页数','data':result[0]}
        logger.info('<---数据查询完成 返回参数:{0}--->'.format(data))
        return HttpResponse(json.dumps(data),content_type='application/json')
    except Exception as e :
        logger.info("<---异常信息:{0}  发生异常的行数:{1}--->".format(e.__traceback__.tb_lineno))
        data = {'code':2,'msg':"<---异常信息:{0}  发生异常的行数:{1}--->".format(e.__traceback__.tb_lineno),'data':'Failure'}
        return HttpResponse(json.dumps(data),content_type='application/json')


#数据分页
def Data_Pagination(page,pagesize,result):
    logger.info('<---调用数据分页---->')
    paginator = Paginator(result,pagesize)
    try:
        if int(page) == 0 : page =1
        result_pag = paginator.page(int(page))
    except PageNotAnInteger:
        result_pag = paginator.page(1)
    except EmptyPage:
        # result_pag = paginator.page(paginator.num_pages)
        result_pag = []
    except Exception as e :
        logger.info('<---数据分页接口异常 异常信息:{0} 异常发生代码行数:{1}--->'.format(e,e.__traceback__.tb_lineno))

    return result_pag,paginator.count


#删除主机信息
def Del_HostInfo(request):
    try:
        logger.info('<---调用删除主机信息接口---->')
        body = json.loads(request.body.decode())
        logger.info('<---接收的参数:{}---->'.format(body))
        id_list = body.get('id_list',[])
        if id_list:
            del_influence_num = HostInfoManage.objects.filter(id__in=id_list)
            if del_influence_num.exists():
                del_influence_num.delete()
                logger.info('<---id下主机数据删除完成--->')
                data = {'code':1,'msg':'id下主机数据删除完成','data':'success'}
                return HttpResponse(json.dumps(data),content_type='application/json')
            else:
                data = {'code':2,'msg':'列表为空 无id参数','data':'Failure'}
                return HttpResponse(json.dumps(data),content_type='application/json')
        else:
            data = {'code':2,'msg':'对比主机id不能为空','data':'Failure'}
            return HttpResponse(json.dumps(data),content_type='application/json')

    except Exception as e :
        logger.info("<---异常信息:{0}  发生异常的行数:{1}--->".format(e.__traceback__.tb_lineno))
        data = {'code':2,'msg':"<---异常信息:{0}  发生异常的行数:{1}--->".format(e.__traceback__.tb_lineno),'data':'Failure'}
        return HttpResponse(json.dumps(data),content_type='application/json')

#修改主机信息
def Upd_HostInfo(request):
    logger.info('<---修改主机信息接口调用---->')
    body = json.loads(request.body.decode())
    try:
        logger.info('<---接收的参数:{}---->'.format(body))
        id = body.get('id','')
        hostname = body.get('hostname','')
        hostgroup = body.get('hostgroup','')
        hostip = body.get('hostip','')
        port = body.get('port','')
        credential = body.get('credential','')
        description = body.get('description','')
        hoststatus = body.get('hoststatus','')
        if id != '':
            sel_influence_num = HostInfoManage.objects.filter(id=int(id))
            if sel_influence_num.exists():
                upd_influence_num = sel_influence_num.update(hostname=hostname,hostgroup=hostgroup,hostip=hostip,port=int(port),
                                                             credential=credential,description=description,hoststatus=int(hoststatus))
                if upd_influence_num == 1:
                    logger.info('<---id:{0}的数据更新成功--->'.format(id))
                    data = {'code':1,'msg':'id:{0}的数据更新成功'.format(id),'data':'success'}
                    return HttpResponse(json.dumps(data),content_type='application/json')
                else:
                    data = {'code':2,'msg':'id:{0}的数据库更新失败'.format(id),'data':'Failure'}
                    return HttpResponse(json.dumps(data),content_type='application/json')
            else:
                data = {'code':2,'msg':'没有找到id:{0}的数据'.format(id),'data':'Failure'}
                return HttpResponse(json.dumps(data),content_type='application/json')
        else:
            data = {'code':2,'msg':'对比主机id不能为空','data':'Failure'}
            return HttpResponse(json.dumps(data),content_type='application/json')
    except Exception as e :
        logger.info("<---异常信息:{0}  发生异常的行数:{1}--->".format(e.__traceback__.tb_lineno))
        data = {'code':2,'msg':"<---异常信息:{0}  发生异常的行数:{1}--->".format(e.__traceback__.tb_lineno),'data':'Failure'}
        return HttpResponse(json.dumps(data),content_type='application/json')

