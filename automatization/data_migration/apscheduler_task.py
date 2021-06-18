#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#@time:
#@Author:lsy
#@file:
#@function:-----------


from apscheduler.schedulers.background import BackgroundScheduler,BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
from threading import Thread
from .views import *
from automatization.settings import logger
from .models import Databases_Migration_Task,File_Migration_Task,Implement_Status_Task
import os
import datetime
import time
import json


def My_APScheduler_Task(**kwargs):
    try:
        current_datetime = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S")
        logger.info('<----定时任务启动接收的参数为:{0},日期:{1}--->'.format(kwargs,current_datetime))
        task_id = kwargs['task_id']
        task_type = int(kwargs['task_type'])
        task_imp_operation = int(kwargs['task_imp_operation'])
        task_imp_interval = int(kwargs['task_imp_interval'])
        task_imp_time = kwargs['task_imp_time']

        task_count = Implement_Status_Task.objects.filter(task_id=task_id)
        logger.info('<----定时任务历史条数:{0}--->'.format(task_count.count()))
        if task_count.count() == 1 and  task_count[0].task_status == 0:
            key_id = task_count[0].id
            task_count.update(task_status=1)
        else:
            implement_status_task = Implement_Status_Task()
            implement_status_task.task_id = task_id
            implement_status_task.task_type = task_type
            implement_status_task.task_imp_operation = task_imp_operation
            implement_status_task.task_imp_interval = task_imp_interval
            implement_status_task.task_imp_time = task_imp_time
            implement_status_task.task_status = 1
            implement_status_task.task_desc = "任务执行中"
            implement_status_task.save()

            key_id = implement_status_task.id

        logger.info('<----任务状态表主键id:{0}--->'.format(key_id))
        if task_id[0:4] == 'DBMG':
            db_result_parameter = Databases_Migration_Task.objects.get(task_id=task_id)
            body = {
                    "db_ip":db_result_parameter.db_ip,
                    "db_username":db_result_parameter.db_username,
                    "db_password":db_result_parameter.db_password,
                    "db_port":int(db_result_parameter.db_port),
                    "db_name":db_result_parameter.db_name,
                    "db_tablename":eval(db_result_parameter.db_tablename),
                    "filepath":db_result_parameter.filepath,
                    "db_ip_lg":db_result_parameter.db_ip_lg,
                    "db_username_lg":db_result_parameter.db_username_lg,
                    "db_password_lg":db_result_parameter.db_password_lg,
                    "db_port_lg":int(db_result_parameter.db_port_lg),
                    "db_name_lg":db_result_parameter.db_name_lg
            }
            logger.info('<---传入数据迁移方法 任务类型task_type:{0} 参数:{1}--->'.format(task_type,body))
            print(body)
            if task_type == 1:
                Long_Range_File_Implement(body,key_id)
            elif task_type == 2:
                Databases_Generate_File(body,key_id)
            else:
                logger.info('<---数据库迁移还没有该任务类型：{0}--->'.format(task_type))

        elif task_id[0:4] == 'FLMG':
            file_result_parameter = File_Migration_Task.objects.get(task_id=task_id)
            body = {
                # "task_type":file_result_parameter.task_type,
                "source_ip":file_result_parameter.source_ip,
                "source_user":file_result_parameter.source_user,
                "source_pwd":file_result_parameter.source_pwd,
                "source_path":file_result_parameter.source_path,
                "local_path":file_result_parameter.local_path,
                "backups_path":file_result_parameter.backups_path,
                "interval_date":int(file_result_parameter.interval_date),
                "date_type":int(file_result_parameter.date_type),
                "long_range_ip":file_result_parameter.long_range_ip,
                "long_range_user":file_result_parameter.long_range_user,
                "long_range_pwd":file_result_parameter.long_range_pwd
            }
            logger.info('<----传入文件迁移方法 任务类型task_type:{0} 参数:{1}--->'.format(task_type,body))
            print(body)
            if task_type == 3:
                Backups_File(body,key_id)
            elif task_type == 4:
                Long_Range_Move_File(body,key_id)
            else:
                logger.info('<----文件迁移没有该任务种类 task_type:{}--->'.format(task_type))
        Implement_Status_Task.objects.filter(id=key_id).update(task_status=2,task_desc='任务执行完成')
    except Exception as e:
        if task_id:
            logger.info('<----处理迁移任务异常 task_id:{0} 异常信息:{1} 报错行数:{2}--->'.format(task_id,e,e.__traceback__.tb_lineno))
            Implement_Status_Task.objects.filter(id=key_id).update(task_status=3,task_desc='任务执行失败  详细请看日志')


# 定义一个异步的线程
def async_t(fun):
    def wrapper(*args,**kwargs):
        thr = Thread(target=fun,args=args,kwargs=kwargs)
        thr.start()
    return wrapper

#更新任务表 (触发定时任务)
def Upd_Implement_Status_Task(request):
    logger.info('<---调用接口更新任务表 (触发定时任务)---->')
    body = json.loads(request.body.decode())
    logger.info('<---接收的参数:{}---->'.format(body))
    task_id = body.get('id','')
    task_type = body.get('task_type','')
    task_operation = body.get('task_operation',0)
    task_imp_operation = body.get('task_imp_operation','')
    task_imp_interval = body.get('task_imp_interval','')
    task_imp_time = body.get('task_imp_time','')
    #新增
    if task_operation == 0 or task_operation == 1:
        Upd_Implement_Status_Task_Async(task_id,task_type,task_imp_operation,task_imp_interval,task_imp_time,task_operation)
    #删除
    elif task_operation == 2:
        run(task_id,task_type,task_imp_operation,task_imp_interval,task_imp_time,task_operation)
    else:
        logger.info('<---该任务操作类型不存在:{0}---->'.format(task_operation))
        data = {'code':2,'msg':'该任务操作类型不存在:{0}'.format(task_operation),'data':'Failure'}
        return HttpResponse(json.dumps(data),content_type='application/json')

    logger.info('<---任务id:{0}的数据任务执行开始---->'.format(task_id))
    data = {'code':1,'msg':'任务id:{0}的数据任务执行开始'.format(task_id),'data':'success'}
    return HttpResponse(json.dumps(data),content_type='application/json')


'''修改任务信息（获取定时参数 执行定时任务）'''
@async_t
def Upd_Implement_Status_Task_Async(task_id,task_type,task_imp_operation,task_imp_interval,task_imp_time,task_operation):
# def Upd_Implement_Status_Task(request):
    logger.info('<---修改任务信息接口（获取定时参数 执行定时任务）---->')
    # body = json.loads(request.body.decode())
    try:
        # # logger.info('<---接收的参数:{}---->'.format(request.POST))
        # task_id = body.get('id','')
        # task_imp_operation = body.get('task_imp_operation','')
        # task_imp_interval = body.get('task_imp_interval','')
        # task_imp_time = body.get('task_imp_time','')

        if task_id != '':
            sel_influence_num = Implement_Status_Task.objects.filter(task_id=task_id)
            if sel_influence_num.count() == 1:
                upd_influence_num = sel_influence_num.update(task_imp_operation = task_imp_operation,task_imp_interval = task_imp_interval,task_imp_time = task_imp_time)
                if upd_influence_num == 1:
                    logger.info('任务id:{0}的数据 定时参数更新完成'.format(task_id))
                    #调用定时任务(阻塞模式)
                    run(task_id,task_type,task_imp_operation,task_imp_interval,task_imp_time,task_operation)
            elif sel_influence_num.count() >1:
                logger.info('任务id:{0}的数据 再次启动完成'.format(task_id))
                run(task_id,task_type,task_imp_operation,task_imp_interval,task_imp_time,task_operation)
            else:
                logger.info('没有找到任务id:{0}的数据'.format(task_id))
        else:
            logger.info('<---数据迁移任务id不能为空--->')
    except Exception as e :
        logger.info('<---数据迁移更新接口异常 异常信息:{0} 异常发生代码行数:{1}--->'.format(e,e.__traceback__.tb_lineno))



# def Del_Implement_Status_Task(request):
#     try:
#         body = json.loads(request.body.decode())
#         task_id = body.get('task_id','')
#         if task_id:
#
#         else:
#             data = {'code':2,'msg':'请输入需要停止的任务id','data':'Failure'}
#             return HttpResponse(json.dumps(data),content_type='application/json')
#     except Exception as e:
#         pass
#
#测试的方法
def test(**kwargs):
    logger.info("-------------{},{}".format(time.ctime(),kwargs))
    print("-------------{},{}".format(time.ctime(),kwargs))

def run(task_id,task_type,task_imp_operation,task_imp_interval,task_imp_time,task_operation):
    try:
        logger.info('<----手动定时任务启动参数(第一次启动)：task_id:{0},task_type:{1},task_imp_operation:{2},task_imp_interval:{3},task_imp_time{4},task_operation{5}--->'
                   .format(task_id,task_type,task_imp_operation,task_imp_interval,task_imp_time,task_operation))
        print(task_id,task_type,task_imp_operation,task_imp_interval,task_imp_time,task_operation)
        executors = {
            'default' : ThreadPoolExecutor(20)
        }

        scheduler = BlockingScheduler(executors=executors)
        #weeks=0, days=0, hours=0, minutes=0, seconds=0,
        if task_imp_operation == 1:
            if task_imp_interval == 1:
                Trigger = IntervalTrigger(seconds = int(task_imp_time))
            elif task_imp_interval == 2:
                Trigger = IntervalTrigger(minutes = int(task_imp_time))
            elif task_imp_interval == 3:
                Trigger = IntervalTrigger(hours=int(task_imp_time))
            elif task_imp_interval == 4:
                Trigger = IntervalTrigger(days=int(task_imp_time))
            else:
                Trigger = IntervalTrigger(weeks=int(task_imp_time))

            logger.info("<---时间间隔模式 类型:{0} 间隔:{1}--->".format(task_imp_interval,task_imp_time))
        elif task_imp_operation == 2:
            Trigger = DateTrigger(task_imp_time)

            logger.info("<---时间点模式 类型:{0} 时间点:{1}--->".format(task_imp_operation,task_imp_time))
        elif task_imp_operation == 3:
            '''
            year (int|str) – 年，4位数字
            month (int|str) – 月 (范围1-12)
            day (int|str) – 日 (范围1-31)
            week (int|str) – 周 (范围1-53)
            day_of_week (int|str) – 周内第几天或者星期几 (范围0-6 或者 mon,tue,wed,thu,fri,sat,sun)
            hour (int|str) – 时 (范围0-23)
            minute (int|str) – 分 (范围0-59)
            second (int|str) – 秒 (范围0-59)
            start_date (datetime|str) – 最早开始日期(包含)
            end_date (datetime|str) – 最晚结束时间(包含)
            timezone (datetime.tzinfo|str) – 指定时区
            '''
            #{"month":1,"week":1,"day":1,"hour":1,"minute":1,"second":1}
            date_para = eval(task_imp_time)
            corn_date = {k:v  if date_para.get(k,"") != "" else None for k,v in date_para.items()}
            Trigger = CronTrigger(year=corn_date.get("year",None),month=corn_date.get("month",None),week=corn_date.get("week",None),day=corn_date.get("day",None),
                                  hour=corn_date.get("hour",None),minute=corn_date.get("minute",None),second=corn_date.get("second",None),
                                  day_of_week=corn_date.get("day_of_week",None),start_date=corn_date.get("start_date",None),end_date=corn_date.get("end_date",None))

            logger.info('<----unix corn 模式:{0} 定时参数:{1}--->'.format(task_imp_operation,corn_date))
        else:
            logger.info('<----该定时任务种类暂不存在：{}--->'.format(task_imp_operation))
        scheduler.add_job(
             # My_APScheduler_Task,
             test,
             Trigger,
             coalesce=False,
             kwargs={"task_id": task_id,"task_type":task_type,"task_imp_operation":task_imp_operation,
                    "task_imp_interval":task_imp_interval,"task_imp_time":task_imp_time},
             id=task_id
        )
        if task_operation == 0 or task_operation == 1:
            logger.info('<----启动任务--->')
            scheduler.start()
        else:
            # print(task_id)
            lp = scheduler.remove_job(job_id=task_id)
            print(lp)
            print(scheduler.get_jobs())
            # scheduler.start()
            data = {'code':2,'msg':'该任务删除成功','data':'Failure'}
            return HttpResponse(json.dumps(data),content_type='application/json')
    except Exception as e:
        logger.info('<----定时任务启动异常 task_id:{0} 异常信息:{1} 报错行数:{2}--->'.format(task_id,e,e.__traceback__.tb_lineno))