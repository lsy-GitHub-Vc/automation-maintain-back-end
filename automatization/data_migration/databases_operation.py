#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#@time:
#@Author:lsy
#@file:
#@function:-----------
from .models import Databases_Migration_Task,File_Migration_Task,Implement_Status_Task
from django.http import HttpResponse
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
import json
import datetime
import time
from automatization.settings import logger


#添加数据库迁移信息
def Ins_Databases_Migration_Task(request):
    try:
        logger.info('<---调用添加数据库迁移信息接口--->')
        body = json.loads(request.body.decode())

        logger.info('<---接口接收参数:{0}--->'.format(body))
        task_type = body.get('task_type','')
        db_ip = body.get('db_ip','')
        db_username = body.get('db_username','')
        db_password = body.get('db_password','')
        db_port = body.get('db_port',0)
        db_name = body.get('db_name','')
        db_tablename = body.get('db_tablename','')
        filepath = body.get('filepath','')
        db_ip_lg = body.get('db_ip_lg','')
        db_username_lg = body.get('db_username_lg','')
        db_password_lg = body.get('db_password_lg','')
        db_port_lg = body.get('db_port_lg',0)
        db_name_lg = body.get('db_name_lg','')

        #添加任务表
        task_id = 'DBMG'+str(datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M%S%f"))
        databases_migration_task = Databases_Migration_Task()
        databases_migration_task.task_id = task_id
        databases_migration_task.task_type = task_type
        databases_migration_task.db_ip = db_ip
        databases_migration_task.db_username = db_username
        databases_migration_task.db_password = db_password
        databases_migration_task.db_port = db_port
        databases_migration_task.db_name = db_name
        databases_migration_task.db_tablename = db_tablename
        databases_migration_task.filepath = filepath
        databases_migration_task.db_ip_lg = db_ip_lg
        databases_migration_task.db_username_lg = db_username_lg
        databases_migration_task.db_password_lg = db_password_lg
        databases_migration_task.db_port_lg = db_port_lg
        databases_migration_task.db_name_lg = db_name_lg
        databases_migration_task.save()

        #添加状态表
        implement_status_task = Implement_Status_Task()
        # implement_status_task.task_id = databases_migration_task.id
        implement_status_task.task_id = task_id
        implement_status_task.task_type = task_type   # # 任务类型 定义调用的方法   1：数据库远端到远端 2：数据库远端数据备份  3 文件移动 4 文件远端到远端
        implement_status_task.task_status = 0 # 执行状态 0:待执行 1:执行中 2:执行成功 3:执行失败 4:
        implement_status_task.task_desc = '任务待执行'
        implement_status_task.save()

        logger.info('<---任务添加成功--->')
        data = {'code':1,'msg':'任务添加成功','data':'success'}
        return HttpResponse(json.dumps(data),content_type='application/json')
    except Exception as e:
        logger.info('<---添加迁移信息接口异常 异常信息:{0} 异常发生代码行数:{1}--->'.format(e,e.__traceback__.tb_lineno))
        data = {'code':2,'msg':'<---数据迁移参数添加接口异常 异常信息:{0} 异常发生代码行数:{1}--->'.format(e,e.__traceback__.tb_lineno),'data':'Failure'}
        return HttpResponse(json.dumps(data),content_type='application/json')

#删除数据库迁移信息
def Del_Databases_Migration_Task(request):
    try:
        logger.info('<---调用删除数据库迁移信息接口--->')
        body = json.loads(request.body.decode())
        logger.info('<---接收的参数:{}---->'.format(body))
        id = body.get('id','')
        if id != '':
            del_influence_num = Databases_Migration_Task.objects.filter(id=int(id))
            if del_influence_num.exists():
                del_influence_num.delete()
                logger.info('<---id:{0}的数据删除完成--->'.format(id))
                data = {'code':1,'msg':'id:{0}的数据删除完成'.format(id),'data':'success'}
                return HttpResponse(json.dumps(data),content_type='application/json')
            else:
                data = {'code':2,'msg':'没有找到id:{0}的数据'.format(id),'data':'Failure'}
                return HttpResponse(json.dumps(data),content_type='application/json')
        else:
            data = {'code':2,'msg':'数据库迁移id不能为空','data':'Failure'}
            return HttpResponse(json.dumps(data),content_type='application/json')

    except Exception as e :
        logger.info('<---删除迁移信息接口异常 异常信息:{0} 异常发生代码行数:{1}--->'.format(e,e.__traceback__.tb_lineno))
        data = {'code':2,'msg':'<---数据迁移参数删除接口异常 异常信息:{0} 异常发生代码行数:{1}--->'.format(e,e.__traceback__.tb_lineno),'data':'Failure'}
        return HttpResponse(json.dumps(data),content_type='application/json')



#修改迁移信息
def Upd_Databases_Migration_Task(request):
    logger.info('<---修改迁移信息接口调用---->')
    body = json.loads(request.body.decode())
    try:
        logger.info('<---接收的参数:{}---->'.format(body))
        id = body.get('id','')
        task_type = body.get('task_type','')
        db_ip = body.get('db_ip','')
        db_username = body.get('db_username','')
        db_password = body.get('db_password','')
        db_port = body.get('db_port',0)
        db_name = body.get('db_name','')
        db_tablename = body.get('db_tablename','')
        filepath = body.get('filepath','')
        db_ip_lg = body.get('db_ip_lg','')
        db_username_lg = body.get('db_username_lg','')
        db_password_lg = body.get('db_password_lg','')
        db_port_lg = body.get('db_port_lg',0)
        db_name_lg = body.get('db_name_lg','')

        if id != '':
            sel_influence_num = Databases_Migration_Task.objects.filter(id=int(id))
            if sel_influence_num.exists():
                upd_influence_num = sel_influence_num.update(db_ip = db_ip,task_type = task_type,db_username = db_username,db_password = db_password,db_port = int(db_port),db_name = db_name,
                                                             db_tablename = db_tablename,filepath = filepath,db_ip_lg = db_ip_lg,db_username_lg = db_username_lg,
                                                             db_password_lg = db_password_lg,db_port_lg = int(db_port_lg),db_name_lg = db_name_lg,)
                if upd_influence_num == 1:
                    logger.info('<---id:{0}的数据更新成功---->'.format(id))
                    data = {'code':1,'msg':'id:{0}的数据更新成功'.format(id),'data':'success'}
                    return HttpResponse(json.dumps(data),content_type='application/json')
                else:
                    data = {'code':2,'msg':'id:{0}的数据库更新失败'.format(id),'data':'Failure'}
                    return HttpResponse(json.dumps(data),content_type='application/json')
            else:
                data = {'code':2,'msg':'没有找到id:{0}的数据'.format(id),'data':'Failure'}
                return HttpResponse(json.dumps(data),content_type='application/json')

        else:
            data = {'code':2,'msg':'数据迁移id不能为空','data':'Failure'}
            return HttpResponse(json.dumps(data),content_type='application/json')
    except Exception as e :
        logger.info('<---修改迁移信息接口异常 异常信息:{0} 异常发生代码行数:{1}--->'.format(e,e.__traceback__.tb_lineno))
        data = {'code':2,'msg':'<---数据迁移参数修改接口异常 异常信息:{0} 异常发生代码行数:{1}--->'.format(e,e.__traceback__.tb_lineno),'data':'Failure'}
        return HttpResponse(json.dumps(data),content_type='application/json')

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
        logger.info('<---数据分页接口异常 异常信息:{0} 异常发生代码行数:{1}--->'.format(e,e.__traceback__.tb_lineno))

    return result_pag,paginator.count


#查询迁移信息
def Sel_Databases_Migration_Task(request):
    try:
        logger.info('<---调用查询迁移信息接口--->')
        logger.info('<---获取的参数:{0}--->'.format(request.GET))
        #获取页码
        page = request.GET.get('page',1)
        pagesize = int(request.GET.get('pagesize',15))
        db_ip = request.GET.get('db_ip','')
        db_ip_lg = request.GET.get('db_ip_lg','')
        db_name = request.GET.get('db_name','')
        db_name_lg = request.GET.get('db_name_lg','')
        result_list = []
        if db_ip:
            sel_influence_result = Databases_Migration_Task.objects.filter(db_ip=db_ip)
            if sel_influence_result.exists():
                result = Data_Pagination(page,pagesize,sel_influence_result)
            else:
                data = {'code':2,'msg':'没有找到主机名db_ip:{} 对应的数据'.format(db_ip),'data':'Failure'}
                return HttpResponse(json.dumps(data),content_type='application/json')
        elif db_ip_lg:
            sel_influence_result = Databases_Migration_Task.objects.filter(db_ip_lg=db_ip_lg)
            if sel_influence_result.exists():
                result = Data_Pagination(page,pagesize,sel_influence_result)
            else:
                data = {'code':2,'msg':'没有找到主机地址db_ip_lg:{} 对应的数据'.format(db_ip_lg),'data':'Failure'}
                return HttpResponse(json.dumps(data),content_type='application/json')
        elif db_name:
            sel_influence_result = Databases_Migration_Task.objects.filter(db_name=db_name)
            if sel_influence_result.exists():
                result = Data_Pagination(page,pagesize,sel_influence_result)
            else:
                data = {'code':2,'msg':'没有找到库名db_name:{} 对应的数据'.format(db_name),'data':'Failure'}
                return HttpResponse(json.dumps(data),content_type='application/json')
        elif db_name_lg:
            sel_influence_result = Databases_Migration_Task.objects.filter(db_name_lg=db_name_lg)
            if sel_influence_result.exists():
                result = Data_Pagination(page,pagesize,sel_influence_result)
            else:
                data = {'code':2,'msg':'没有找到库名db_name_lg:{} 对应的数据'.format(db_name_lg),'data':'Failure'}
                return HttpResponse(json.dumps(data),content_type='application/json')
        else:
            sel_influence_result = Databases_Migration_Task.objects.all()
            if sel_influence_result.exists():
                result = Data_Pagination(page,pagesize,sel_influence_result)
            else:
                data = {'code':2,'msg':'没有找到数据信息','data':'Failure'}
                return HttpResponse(json.dumps(data),content_type='application/json')

        # logger.info('<---返回的分页数据:{}--->'.format(result))
        if result[0]:
            for result_sing in result[0]:
                result_list.append({'id':result_sing.id,'task_id':result_sing.task_id,'task_type':result_sing.task_type,'db_ip':result_sing.db_ip,'create_time':datetime.datetime.strftime(result_sing.create_time,"%Y-%m-%d %H:%M:%S.%f"),'db_username':result_sing.db_username,
                                    'db_password':result_sing.db_password,'db_port':result_sing.db_port,'db_name':result_sing.db_name,'db_tablename':result_sing.db_tablename,'filepath':result_sing.filepath,'db_ip_lg':result_sing.db_ip_lg,
                                    'db_username_lg':result_sing.db_username_lg,'db_password_lg':result_sing.db_password_lg,'db_port_lg':result_sing.db_port_lg,'db_name_lg':result_sing.db_name_lg})
            data = {'code':1,'msg':'数据查询完成','total':result[1],'data':result_list}
        else:
            data = {'code':2,'msg':'已达最大页数','data':result[0]}

        logger.info('<---数据查询：{}---->'.format(data))
        return HttpResponse(json.dumps(data),content_type='application/json')
    except Exception as e :
        logger.info('<---查询数据迁移信息接口异常 异常信息:{0} 异常发生代码行数:{1}--->'.format(e,e.__traceback__.tb_lineno))
        data = {'code':2,'msg':'<---查询数据迁移信息接口异常 异常信息:{0} 异常发生代码行数:{1}--->'.format(e,e.__traceback__.tb_lineno),'data':'Failure'}
        return HttpResponse(json.dumps(data),content_type='application/json')

#查询历史执行信息
def Sel_Implement_Status_Task(request):
    try:
        logger.info('<---调用查询历史执行信息接口--->')
        logger.info('<---获取的参数:{0}--->'.format(request.GET))
        #获取页码
        page = request.GET.get('page',1)
        pagesize = int(request.GET.get('pagesize',15))
        task_id = request.GET.get('task_id','')
        result_list = []
        if task_id:
            sel_influence_result = Implement_Status_Task.objects.filter(task_id=task_id).order_by('-id')
            if sel_influence_result.exists():
                result = Data_Pagination(page,pagesize,sel_influence_result)
            else:
                data = {'code':2,'msg':'没有找到任务id:{} 对应的数据'.format(task_id),'data':'Failure'}
                return HttpResponse(json.dumps(data),content_type='application/json')
        else:
            data = {'code':2,'msg':'任务id不能为空','data':'Failure'}
            return HttpResponse(json.dumps(data),content_type='application/json')

        # logger.info('<---返回的分页数据:{}--->'.format(result))
        if result[0]:
            for result_sing in result[0]:
                result_list.append({'id':result_sing.id,'task_id':result_sing.task_id,'create_time':datetime.datetime.strftime(result_sing.create_time,"%Y-%m-%d %H:%M:%S.%f"),
                                    'task_imp_operation':result_sing.task_imp_operation,'task_imp_interval':result_sing.task_imp_interval,
                                    'task_imp_time':result_sing.task_imp_time,'task_type':result_sing.task_type,
                                    'task_status':result_sing.task_status,'task_desc':result_sing.task_desc})
            data = {'code':1,'msg':'数据查询完成','total':result[1],'data':result_list}
        else:
            data = {'code':2,'msg':'已达最大页数','data':result[0]}
        logger.info('<---数据查询：{}---->'.format(data))
        return HttpResponse(json.dumps(data),content_type='application/json')
    except Exception as e :
        logger.info('<---查询历史任务信息接口异常 异常信息:{0} 异常发生代码行数:{1}--->'.format(e,e.__traceback__.tb_lineno))
        data = {'code':2,'msg':'<---查询历史任务信息接口异常 异常信息:{0} 异常发生代码行数:{1}--->'.format(e,e.__traceback__.tb_lineno),'data':'Failure'}
        return HttpResponse(json.dumps(data),content_type='application/json')

#添加文件迁移信息
def Ins_File_Migration_Task(request):
    try:
        logger.info('<---调用添加文件迁移信息接口--->')
        body = json.loads(request.body.decode())
        logger.info('<---获取的参数:{0}--->'.format(body))
        task_type = body.get('task_type','')
        source_ip = body.get('source_ip','')
        source_user = body.get('source_user','')
        source_pwd = body.get('source_pwd','')
        source_path = body.get('source_path','')
        interval_date = body.get('interval_date','')
        date_type = body.get('date_type','')
        local_path = body.get('local_path','')
        long_range_ip = body.get('long_range_ip','')
        long_range_user = body.get('long_range_user','')
        long_range_pwd = body.get('long_range_pwd','')
        backups_path = body.get('backups_path','')

        #添加任务表
        task_id = str("FLMG"+datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M%S%f"))
        file_migration_task = File_Migration_Task()
        file_migration_task.task_id = task_id
        file_migration_task.task_type = task_type
        file_migration_task.source_ip = source_ip
        file_migration_task.source_user = source_user
        file_migration_task.source_pwd = source_pwd
        file_migration_task.source_path = source_path
        file_migration_task.interval_date = interval_date
        file_migration_task.date_type = date_type
        file_migration_task.local_path = local_path
        file_migration_task.long_range_ip = long_range_ip
        file_migration_task.long_range_user = long_range_user
        file_migration_task.long_range_pwd = long_range_pwd
        file_migration_task.backups_path = backups_path
        file_migration_task.save()


        #添加状态表
        implement_status_task = Implement_Status_Task()
        implement_status_task.task_id = task_id
        implement_status_task.task_type = task_type   # 任务类型 定义调用的方法   1：数据库远端到远端 2：数据库远端数据备份  3 文件移动 4 文件远端到远端
        implement_status_task.task_status = 0 # 执行状态 0:待执行 1:执行中 2:执行成功 3:执行失败 4:
        implement_status_task.task_desc = '任务待执行'
        implement_status_task.save()

        logger.info('<---任务添加完成---->')
        data = {'code':1,'msg':'任务添加成功','data':'success'}
        return HttpResponse(json.dumps(data),content_type='application/json')
    except Exception as e:
        logger.info('<---调用添加文件迁移信息接口异常 异常信息:{0} 异常发生代码行数:{1}--->'.format(e,e.__traceback__.tb_lineno))
        data = {'code':2,'msg':'<---调用添加文件迁移信息接口异常 异常信息:{0} 异常发生代码行数:{1}--->'.format(e,e.__traceback__.tb_lineno),'data':'Failure'}
        return HttpResponse(json.dumps(data),content_type='application/json')


#删除文件迁移信息
def Del_File_Migration_Task(request):
    try:
        logger.info('<---调用删除文件迁移信息信息接口--->')
        body = json.loads(request.body.decode())
        logger.info('<---接收的参数:{}---->'.format(body))
        id = body.get('id','')
        if id != '':
            del_influence_num = File_Migration_Task.objects.filter(id=int(id))
            if del_influence_num.exists():
                del_influence_num.delete()
                logger.info('<---id:{0}的数据删除完成---->'.format(id))
                data = {'code':1,'msg':'id:{0}的数据删除完成'.format(id),'data':'success'}
                return HttpResponse(json.dumps(data),content_type='application/json')
            else:
                data = {'code':2,'msg':'没有找到id:{0}的数据'.format(id),'data':'Failure'}
                return HttpResponse(json.dumps(data),content_type='application/json')
        else:
            data = {'code':2,'msg':'文件迁移id不能为空','data':'Failure'}
            return HttpResponse(json.dumps(data),content_type='application/json')

    except Exception as e :
        logger.info('<---调用删除文件迁移信息接口异常 异常信息:{0} 异常发生代码行数:{1}--->'.format(e,e.__traceback__.tb_lineno))
        data = {'code':2,'msg':'<---调用删除文件迁移信息接口异常 异常信息:{0} 异常发生代码行数:{1}--->'.format(e,e.__traceback__.tb_lineno),'data':'Failure'}
        return HttpResponse(json.dumps(data),content_type='application/json')

#修改文件迁移信息
def Upd_File_Migration_Task(request):
    try:
        logger.info('<---修改文件迁移信息接口调用---->')
        body = json.loads(request.body.decode())
        logger.info('<---接收的参数:{}---->'.format(body))
        id = body.get('id','')
        task_type = body.get('task_type','')
        source_ip = body.get('source_ip','')
        source_user = body.get('source_user','')
        source_pwd = body.get('source_pwd','')
        source_path = body.get('source_path','')
        local_path = body.get('local_path','')
        interval_date = body.get('interval_date','')
        date_type = body.get('date_type','')
        long_range_ip = body.get('long_range_ip','')
        long_range_user = body.get('long_range_user','')
        long_range_pwd = body.get('long_range_pwd','')
        backups_path = body.get('backups_path','')


        if id != '':
            sel_influence_num = File_Migration_Task.objects.filter(id=int(id))
            if sel_influence_num.exists():
                upd_influence_num = sel_influence_num.update(source_ip = source_ip,source_user = source_user,source_pwd = source_pwd,source_path = source_path,local_path = local_path,interval_date = interval_date,
                                                             date_type = date_type,long_range_ip = long_range_ip,long_range_user = long_range_user,long_range_pwd = long_range_pwd,task_type = task_type,
                                                             backups_path = backups_path)
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
            data = {'code':2,'msg':'文件迁移id不能为空','data':'Failure'}
            return HttpResponse(json.dumps(data),content_type='application/json')
    except Exception as e :
        logger.info('<---调用修改文件迁移信息接口异常 异常信息:{0} 异常发生代码行数:{1}--->'.format(e,e.__traceback__.tb_lineno))
        data = {'code':2,'msg':'<---调用修改文件迁移信息接口异常 异常信息:{0} 异常发生代码行数:{1}--->'.format(e,e.__traceback__.tb_lineno),'data':'Failure'}
        return HttpResponse(json.dumps(data),content_type='application/json')

#查询文件迁移信息
def Sel_File_Migration_Task(request):
    try:
        logger.info('<---调用查询文件迁移信息接口调用---->')
        logger.info('<---接收参数:{0}---->'.format(request.GET))
        #获取页码
        page = request.GET.get('page',1)
        pagesize = int(request.GET.get('pagesize',15))
        create_time = request.GET.get('create_time','')
        source_ip = request.GET.get('source_ip','')
        long_range_ip = request.GET.get('long_range_ip','')
        result_list = []
        if create_time:
            create_time_split = create_time.split('-')
            sel_influence_result = File_Migration_Task.objects.filter(create_time__year=create_time_split[0],create_time__month=create_time_split[1],
                                                                      create_time__day=create_time_split[2])

            if sel_influence_result.exists():
                result = Data_Pagination(page,pagesize,sel_influence_result)
            else:
                data = {'code':2,'msg':'没有找到创建时间为:{} 对应的数据'.format(create_time),'data':'Failure'}
                return HttpResponse(json.dumps(data),content_type='application/json')
        elif source_ip:
            sel_influence_result = File_Migration_Task.objects.filter(source_ip=source_ip)
            if sel_influence_result.exists():
                result = Data_Pagination(page,pagesize,sel_influence_result)
            else:
                data = {'code':2,'msg':'没有找源ip为:{} 对应的数据'.format(source_ip),'data':'Failure'}
                return HttpResponse(json.dumps(data),content_type='application/json')
        elif long_range_ip:
            sel_influence_result = File_Migration_Task.objects.filter(long_range_ip=long_range_ip)
            if sel_influence_result.exists():
                result = Data_Pagination(page,pagesize,sel_influence_result)
            else:
                data = {'code':2,'msg':'没有找到目标ip为:{} 对应的数据'.format(long_range_ip),'data':'Failure'}
                return HttpResponse(json.dumps(data),content_type='application/json')
        else:
            sel_influence_result = File_Migration_Task.objects.all()
            if sel_influence_result.exists():
                result = Data_Pagination(page,pagesize,sel_influence_result)
            else:
                data = {'code':2,'msg':'表中没有找到数据','data':'Failure'}
                return HttpResponse(json.dumps(data),content_type='application/json')

        # logger.info('<---返回的分页数据:{}--->'.format(result))
        if result[0]:
            for result_sing in result[0]:
                result_list.append({'id':result_sing.id,'task_id':result_sing.task_id,'task_type':result_sing.task_type,'create_time':datetime.datetime.strftime(result_sing.create_time,"%Y-%m-%d %H:%M:%S.%f"),'source_ip':result_sing.source_ip,
                                    'source_user':result_sing.source_user,'source_pwd':result_sing.source_pwd,'source_path':result_sing.source_path,'local_path':result_sing.local_path,'interval_date':result_sing.interval_date,
                                    'date_type':result_sing.date_type,'long_range_ip':result_sing.long_range_ip,'long_range_user':result_sing.long_range_user,
                                    'long_range_pwd':result_sing.long_range_pwd,'backups_path':result_sing.backups_path})
            data = {'code':1,'msg':'数据查询完成','total':result[1],'data':result_list}
        else:
            data = {'code':2,'msg':'已达最大页数','data':result[0]}
        logger.info('<---数据查询:{0}---->'.format(data))
        return HttpResponse(json.dumps(data),content_type='application/json')
    except Exception as e :
        logger.info('<---调用查询文件迁移信息接口异常 异常信息:{0} 异常发生代码行数:{1}--->'.format(e,e.__traceback__.tb_lineno))
        data = {'code':2,'msg':'<---调用查询文件迁移信息接口异常 异常信息:{0} 异常发生代码行数:{1}--->'.format(e,e.__traceback__.tb_lineno),'data':'Failure'}
        return HttpResponse(json.dumps(data),content_type='application/json')