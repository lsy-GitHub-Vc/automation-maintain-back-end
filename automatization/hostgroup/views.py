#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#@time:
#@Author:lsy
#@file:
#@function:-----------

from automatization.models import HostInfoManage
from django.http import HttpResponse
from io import StringIO
# from automatization.settings import logger
from django.core.paginator import PageNotAnInteger,Paginator,EmptyPage
import json
import os
import xlrd

import pandas as np

def Ins_HostInfo(request):
    try:
        body = json.loads(request.body.decode())

        hostname = body.get('hostname','')
        hostgroup = body.get('hostgroup','')
        hostaddress = body.get('hostaddress','')
        hostport = body.get('hostport','')
        visitproof = body.get('visitproof','')
        describe = body.get('describe','')

        hostinfomanage = HostInfoManage()
        hostinfomanage.hostname = hostname
        hostinfomanage.hostgroup = hostgroup
        hostinfomanage.hostaddress = hostaddress
        hostinfomanage.hostport = hostport
        hostinfomanage.visitproof = visitproof
        hostinfomanage.describe = describe
        hostinfomanage.save()

        data = {'code':1,'msg':'主机信息添加成功','data':'success'}
        return HttpResponse(json.dumps(data),content_type='application/json')
    except Exception as e:
        return HttpResponse(str(e)+"----->异常行数:{0}".format(e.__traceback__.tb_lineno))

#批量插入
def Bulk_Create_HostInfo(request):
    try:
        body = json.loads(request.body.decode())
        filepath = body.get('filepath','')
        sheet_host_list = Execl(filepath)
        # Execl(r'C:\Users\97576\Desktop\host.xlsx')
        #存储插入对象列表
        bulk_create_host_list = []
        for sheet_value_list in sheet_host_list:
            #插入对象
            bulk_create_host_value = HostInfoManage(hostname=sheet_value_list[0],hostgroup=sheet_value_list[1],hostaddress=sheet_value_list[2],
                                                    hostport=sheet_value_list[3],visitproof=sheet_value_list[4],describe=sheet_value_list[5])
            bulk_create_host_list.append(bulk_create_host_value)
        #批量插入
        HostInfoManage.objects.bulk_create(bulk_create_host_list)

        data = {'code':1,'msg':'批量数据插入完成','data':'success'}
        return HttpResponse(json.dumps(data),content_type='application/json')
    except Exception as e:
        return HttpResponse(str(e)+"----->异常行数:{0}".format(e.__traceback__.tb_lineno))

#批量删除
def Bulk_Delete_HostInfo(request):
    try:
        body = json.loads(request.body.decode())
        filepath = body.get('filepath','')
        sheet_host_list = Execl(filepath)
        #存储插入对象列表
        bulk_del_hostname_list = []
        bulk_del_hostaddress_list = []
        for sheet_value_list in sheet_host_list:
            #获取条件列表
            bulk_del_hostname_list.append(sheet_value_list[0])
            bulk_del_hostaddress_list.append(sheet_value_list[2])

        bulk_delete_host_value = HostInfoManage.objects.filter(hostname__in=bulk_del_hostname_list,hostaddress__in=bulk_del_hostaddress_list).delete()

        data = {'code':1,'msg':'批量数据删除完成共:{0}条'.format(bulk_delete_host_value[0]),'data':'success'}
        return HttpResponse(json.dumps(data),content_type='application/json')
    except Exception as e:
        return HttpResponse(str(e)+"----->异常行数:{0}".format(e.__traceback__.tb_lineno))

def Execl(filepath):
    try:
        #判断文件是否存在
        if os.path.isfile(filepath):
            #打开文件
            book = xlrd.open_workbook(filepath)
            sheet_host_list = []
            #所有页
            for sheet in book.sheet_names():
                #读取某一页
                sheet_dt = book.sheet_by_name(sheet)
                #行数
                row = sheet_dt.nrows
                if row > 1:
                    #从第二行开始读 跳过说明行
                    for i in range(row-1):
                        sheet_host_data = sheet_dt.row_values(i+1)
                        sheet_host_list.append(sheet_host_data)
                    return sheet_host_list
                else:
                    data = {'code':2,'msg':'路径文件:{} 无数据'.format(filepath),'data':'Failure'}
                    return HttpResponse(json.dumps(data),content_type='application/json')
        else:
            data = {'code':2,'msg':'路径文件:{} 没有找到文件'.format(filepath),'data':'Failure'}
            return HttpResponse(json.dumps(data),content_type='application/json')
    except Exception as e:
        return HttpResponse(str(e)+"----->异常行数:{0}".format(e.__traceback__.tb_lineno))


def Sel_HostInfo(request):
    #查询主机信息
    try:
        #获取页码
        page = request.GET.get('page',1)
        pagesize = int(request.GET.get('pagesize',15))
        hostname = request.GET.get('hostname','')
        hostaddress = request.GET.get('hostaddress','')
        result_list = []

        if hostname:
            sel_influence_result = HostInfoManage.objects.filter(hostname=hostname)
            if sel_influence_result.exists():
                result = Data_Pagination(page,pagesize,sel_influence_result)
            else:
                data = {'code':2,'msg':'没有找到主机名hostname:{hostname} 对应的数据'.format(hostname),'data':'Failure'}
                return HttpResponse(json.dumps(data),content_type='application/json')
        elif hostaddress:
            sel_influence_result = HostInfoManage.objects.filter(hostaddress=hostaddress)
            if sel_influence_result.exists():
                result = Data_Pagination(page,pagesize,sel_influence_result)
            else:
                data = {'code':2,'msg':'没有找到主机地址hostaddress:{} 对应的数据'.format(hostaddress),'data':'Failure'}
                return HttpResponse(json.dumps(data),content_type='application/json')
        else:
            sel_influence_result = HostInfoManage.objects.all()
            if sel_influence_result.exists():
                result = Data_Pagination(page,pagesize,sel_influence_result)
            else:
                data = {'code':2,'msg':'没有找到数据信息','data':'Failure'}
                return HttpResponse(json.dumps(data),content_type='application/json')

        # logger.info('<---返回的分页数据:{}--->'.format(result))
        if result[0]:
            for result_sing in result[0]:
                result_list.append({'id':result_sing.id,'hostname':result_sing.hostname,'hostgroup':result_sing.hostgroup,'hostaddress':result_sing.hostaddress,
                                    'hostport':result_sing.hostport,'visitproof':result_sing.visitproof,'describe':result_sing.describe,'hoststatus':result_sing.hoststatus})
            data = {'code':1,'msg':'数据查询完成','total':result[1],'data':result_list}
        else:
            data = {'code':2,'msg':'已达最大页数','data':result[0]}
        return HttpResponse(json.dumps(data),content_type='application/json')
    except Exception as e :
        # logger.info('<---类别对比更新接口异常 异常信息:{0} 异常发生代码行数:{1}--->'.format(e,e.__traceback__.tb_lineno))
        return HttpResponse(str(e))

#数据分页
def Data_Pagination(page,pagesize,result):
    # logger.info('<---调用数据分页---->')
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
        # logger.info('<---数据分页接口异常 异常信息:{0} 异常发生代码行数:{1}--->'.format(e,e.__traceback__.tb_lineno))
        return HttpResponse(str(e))

    return result_pag,paginator.count


#删除主机信息
def Del_HostInfo(request):
    try:
        body = json.loads(request.body.decode())
        # logger.info('<---接收的参数:{}---->'.format(request.POST))
        id = body.get('id','')
        if id != '':
            del_influence_num = HostInfoManage.objects.filter(id=int(id))
            if del_influence_num.exists():
                del_influence_num.delete()
                data = {'code':1,'msg':'id:{0}的数据删除完成'.format(id),'data':'success'}
                return HttpResponse(json.dumps(data),content_type='application/json')
            else:
                data = {'code':2,'msg':'没有找到id:{0}的数据'.format(id),'data':'Failure'}
                return HttpResponse(json.dumps(data),content_type='application/json')
        else:
            data = {'code':2,'msg':'对比主机id不能为空','data':'Failure'}
            return HttpResponse(json.dumps(data),content_type='application/json')

    except Exception as e :
        # logger.info('<---删除主机接口异常 异常信息:{0} 异常发生代码行数:{1}--->'.format(e,e.__traceback__.tb_lineno))
        return HttpResponse(str(e))

#修改主机信息
def Upd_HostInfo(request):
    # logger.info('<---修改主机信息接口调用---->')
    body = json.loads(request.body.decode())
    try:
        # logger.info('<---接收的参数:{}---->'.format(request.POST))
        id = body.get('id','')
        hostname = body.get('hostname','')
        hostgroup = body.get('hostgroup','')
        hostaddress = body.get('hostaddress','')
        hostport = body.get('hostport','')
        visitproof = body.get('visitproof','')
        describe = body.get('describe','')
        hoststatus = body.get('hoststatus','')
        if id != '':
            if hostaddress != '':
                sel_influence_num = HostInfoManage.objects.filter(id=int(id))
                if sel_influence_num.exists():
                    upd_influence_num = sel_influence_num.update(hostname=hostname,hostgroup=hostgroup,hostaddress=hostaddress,hostport=int(hostport),
                                                                 visitproof=visitproof,describe=describe,hoststatus=int(hoststatus))
                    if upd_influence_num == 1:
                        data = {'code':1,'msg':'id:{0}的数据更新成功'.format(id),'data':'success'}
                        return HttpResponse(json.dumps(data),content_type='application/json')
                    else:
                        data = {'code':2,'msg':'id:{0}的数据库更新失败'.format(id),'data':'Failure'}
                        return HttpResponse(json.dumps(data),content_type='application/json')
                else:
                    data = {'code':2,'msg':'没有找到id:{0}的数据'.format(id),'data':'Failure'}
                    return HttpResponse(json.dumps(data),content_type='application/json')
            else:
                data = {'code':2,'msg':'主机地址(hostaddress)参数不能为空','data':'Failure'}
                return HttpResponse(json.dumps(data),content_type='application/json')
        else:
            data = {'code':2,'msg':'对比主机id不能为空','data':'Failure'}
            return HttpResponse(json.dumps(data),content_type='application/json')
    except Exception as e :
        # logger.info('<---类别对比更新接口异常 异常信息:{0} 异常发生代码行数:{1}--->'.format(e,e.__traceback__.tb_lineno))
        return HttpResponse(str(e))

