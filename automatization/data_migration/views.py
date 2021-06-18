#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#@time:
#@Author:lsy
#@file:
#@function:-----------
from .models import Implement_Status_Task
from django.http import HttpResponse
from dateutil.relativedelta import relativedelta
import json
import pymysql
import datetime
import time
import re
import os
import shutil
import paramiko
import math
from django.utils import timezone
from automatization.settings import logger

#数据库连接
def Databases_Conn(databases_dict):
    try:
        logger.info("<---数据库连接信息接口 参数:{0}--->".format(databases_dict))

        db_ip = databases_dict.get('db_ip','')
        db_username = databases_dict.get('db_username','')
        db_password = databases_dict.get('db_password','')
        db_port = databases_dict.get('db_port','')
        db_name = databases_dict.get('db_name','')

        #数据库连接
        conn = pymysql.connect(host=db_ip,user=db_username,password=db_password,port=int(db_port),database=db_name,connect_timeout=15,charset="utf8")
        logger.info("<---数据库连接完成--->")
        return conn

    except Exception as e:
        if conn:
            conn.close()
        logger.info("数据库连接---->异常信息{0}---->异常行数{1}".format(str(e),e.__traceback__.tb_lineno))

#连接远程服务
def Long_Rnge_SSH_Clint(long_range_ip,long_range_user,long_range_pwd):
    try:
        logger.info('<---向远端上传文件接口 获取的参数:ip:{0},user:{1},pwd:{2}--->'.format(long_range_ip,long_range_user,long_range_pwd))
        # long_range_ip = body.get('long_range_ip','')
        # long_range_user = body.get('long_range_user','')
        # long_range_pwd = body.get('long_range_pwd','')
        #ssh控制台
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(long_range_ip,22,username=long_range_user,password=long_range_pwd)
        #ssh传输
        transport = paramiko.Transport((long_range_ip,22))
        transport.connect(username=long_range_user,password=long_range_pwd)
        sftp = paramiko.SFTPClient.from_transport(transport)
        logger.info("<---获取远端连接信息完成--->")
        return ssh,sftp
    except Exception as e:
        if transport:
            transport.close()
        if ssh:
            ssh.close()
        logger.info("<---异常信息:{}  行数:{}-->".format(e,e.__traceback__.tb_lineno))
        # data = {'code':2,'msg':"<---异常信息{}  行数{}-->".format(e,e.__traceback__.tb_lineno),'data':'Failure'}
        # return HttpResponse(json.dumps(data),content_type='application/json')

#判断表是否在库中
def table_exists(con, table_name):
    logger.info("<---判断表是否在库中 接口 要验证的表名:{0}--->".format(table_name))
    sql = "show tables;"
    con.execute(sql)
    tables = [con.fetchall()]
    table_list = re.findall('(\'.*?\')', str(tables))
    table_list = [re.sub("'", '', each) for each in table_list]
    if table_name in table_list:
        logger.info("<--- 要验证的表名:{0} 数据库中含有该表--->".format(table_name))
        # 存在返回1
        return 1
    else:
        logger.info("<--- 要验证的表名:{0} 数据库中没有含有该表--->".format(table_name))
        # 不存在返回0
        return 0

#判断日期类型
def Date_Format(dateformat,desc):
    try:
        logger.info('<---判断日期类型接口--->:验证类型:{0} 表结构:{1}'.format(dateformat,desc))
        datedesc = [a for a in desc if dateformat == a[0]]
        print(datedesc)
        if datedesc:
            if datedesc[0][1].find('varchar')==0:
                logger.info('<---判断日期类型--->:验证类型:str')
                return 'str'
            elif datedesc[0][1].find('datetime') == 0:
                logger.info('<---判断日期类型--->:验证类型:datetime')
                return 'date'
            else:
                logger.info('<---确认日期字段类型--->:字段类型 {}'.format(datedesc[0][2]))
                return "fai"
        else:
            logger.info('<---没找到该日期字段--->:字段 {}'.format(dateformat))
            return 'fai'
    except Exception as e:
        logger.info('<---日期类型判断异常--->:字段 {}'.format(dateformat))
        return 'fai'


#生成数据库备份文件
def Databases_File_Write(db_tablename,filepath,conn,key_id=None):
    try:
        logger.info("<---数据库文件写入接口 接收参数:表名:{0} 文件地址:{1} 连接信息:{2}--->".format(db_tablename,filepath,conn))
        cursor = conn.cursor()
        filepath_list = []
        # data = cursor.execute("select * from host_info_manage")
        for item in db_tablename:
            print(item)
            tbname = item.get('tbname','')
            tbdate = item.get('tbdate','')
            if (table_exists(cursor, tbname) == 1):
                cursor.execute("desc {0}".format(tbname))
                descdatabases = cursor.fetchall()
                #找出主键

                #结构信息
                desc_join_glo = ','.join([b[0] for b in descdatabases])
                tag = Date_Format(tbdate,descdatabases)
                #读数据
                #定义日期条件
                date_new = datetime.datetime.now()
                str_start_time = (date_new-relativedelta(months=int(item.get('start_interval',0)))).strftime("%Y%m%d%H%M%S")
                str_end_time = (date_new-relativedelta(months=int(item.get('end_interval',0)))).strftime("%Y%m%d%H%M%S")
                date_start_time = (date_new-relativedelta(months=int(item.get('start_interval',0)))).strftime("%Y-%m-%d %H:%M:%S")
                date_end_time = (date_new-relativedelta(months=int(item.get('end_interval',0)))).strftime("%Y-%m-%d %H:%M:%S")
                page = 1
                pagesiz = 500
                while True:
                    if tag == 'date':
                        if item.get('start_interval',0) == 0:
                            sql_str = "select {0} from {1} where unix_timestamp({2})>=unix_timestamp('{3}') limit {4},{5};".format(desc_join_glo,tbname,tbdate,date_end_time,(page-1)*pagesiz,page*pagesiz)
                        else:
                            sql_str = "select {0} from {1} where unix_timestamp({2})<=unix_timestamp('{3}') and unix_timestamp({4})>=unix_timestamp('{5}') limit {6},{7};".format(desc_join_glo,tbname,tbdate,date_start_time,tbdate,date_end_time,(page-1)*pagesiz,page*pagesiz)
                    elif tag == 'str':
                        if item.get('start_interval',0) == 0:
                            sql_str = 'select {0} from {1} where {2}>={3} limit {4},{5};'.format(desc_join_glo,tbname,tbdate,str_end_time,(page-1)*pagesiz,page*pagesiz)
                        else:
                            sql_str = 'select {0} from {1} where {2}<={3} and {4}>={5} limit {6},{7};'.format(desc_join_glo,tbname,tbdate,str_start_time,tbdate,str_end_time,(page-1)*pagesiz,page*pagesiz)

                    else:
                        logger.info("<---表:{}日期字段非string或datetime-->".format(tbname))
                        break
                    logger.info("<---执行的sql语句:{0}-->".format(sql_str))
                    cursor.execute(sql_str)
                    querydata = cursor.fetchall()

                    if querydata:
                        # if os.path.isdir(r"{0}\{1}".format(filepath,date_new.strftime('%Y%m%d'))) == False:
                        #     os.makedirs(r"{0}\{1}".format(filepath,date_new.strftime('%Y%m%d')))

                        if os.path.isdir(r"{0}".format(filepath)) == False:
                            os.makedirs(r"{0}".format(filepath))
                        path = r"{0}/insert-{1}-{2}.sql".format(filepath,tbname,date_new.strftime('%Y%m%d'))
                        logger.info("<---数据库文件生成地址:{}-->".format(path))
                        # with open(path,'a+') as filewrite:
                        filewrite = open(path,'a+',encoding='utf-8')
                        for querydata_one in querydata:
                            # ins_sql_list_replace = ['null' if y == None else y for y in [i.strftime("%Y-%m-%d %H:%M:%S") if isinstance(i,datetime.datetime) else i for i in querydata_one]]
                            ins_sql_list_replace = []
                            for ins_sql_cs in querydata_one:
                                if isinstance(ins_sql_cs,datetime.datetime):
                                    ins_sql_cs = ins_sql_cs.strftime("%Y-%m-%d %H:%M:%S")
                                if ins_sql_cs == None:
                                    ins_sql_cs = ""
                                ins_sql_list_replace.append(ins_sql_cs)
                            insert_sql = "INSERT INTO {0} ({1})VALUES {2};\n".format(tbname,desc_join_glo,tuple(ins_sql_list_replace))
                            filewrite.write(insert_sql)

                        page +=1
                        logger.info("<---第:{0}笔 备份数据库写入完成--->".format(page-1))
                    else:
                        logger.info("<---表:{0} 写入完成或没有符合的数据--->".format(tbname))
                        if page>1:
                            filepath_list.append(path)
                        if filewrite:
                            filewrite.close()
                        break
            else:
                logger.info("<---没有找到名为:{0}的表-->".format(tbname))
        logger.info("<---生成文件的列表:{0}-->".format(filepath_list))
        return filepath_list
    except Exception as e:
        Implement_Status_Task.objects.filter(id=key_id).update(task_status=3,task_desc='任务执行失败  详细请看日志')
        logger.info("<---异常信息:{}  行数:{}-->".format(e,e.__traceback__.tb_lineno))
    finally:
        if filewrite:
            filewrite.close()
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# monkey.patch_all()
#生成数据库备份文件
def Databases_Generate_File(body,key_id):
    try:
        # body = json.loads(request.body.decode())
        logger.info("<---生成数据库备份文件接口 接收参数:{},状态表id{}--->".format(body,key_id))
        conn = Databases_Conn(body)
        db_tablename = body.get('db_tablename','')
        filepath = body.get('filepath','')
        Databases_File_Write(db_tablename,filepath,conn,key_id)

        logger.info("<------数据库备份文件生成完成------>")
    except Exception as e:
        Implement_Status_Task.objects.filter(id=key_id).update(task_status=3,task_desc='任务执行失败  详细请看日志')
        logger.info("<---异常信息{}  行数{}-->".format(e,e.__traceback__.tb_lineno))
    # finally:
    #     if conn:
    #         conn.close()

#获取符合条件的文件列表
def Check_File(source_path,interval_date,date_type,key_id=None):
    logger.info("<---获取符合条件的文件列表接口 参数:源地址:{0},时间间隔:{1},时间类型:{2},状态表id:{3}--->".format(source_path,interval_date,date_type,key_id))
    try:
        #路径下的文件信息
        dirlist = os.listdir(source_path)
        logger.info("<---路径下的文件列表:{0}--->".format(dirlist))
        if dirlist:
            #拼接为全路径列表
            dir_path_list = [os.path.join(source_path,p) for p in dirlist]
            #过滤掉文件夹
            filelist = [a for a in dir_path_list if os.path.isdir(a)==False]
            logger.info("<---过滤文件夹后的文件列表:{0}--->".format(filelist))
            #获取创建时间

            file_time_dict = {key:'{0}'.format(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(os.path.getctime(key)))) for key in filelist}
            logger.info("<---获取创建时间的集合:{0}--->".format(file_time_dict))

            #当前时间
            current_date = datetime.datetime.now()
            if date_type == 1:
                hanld_date = (current_date-relativedelta(months=int(interval_date))).strftime("%Y-%m-%d %H:%M:%S")
            else:
                hanld_date = (current_date-relativedelta(days=int(interval_date))).strftime("%Y-%m-%d %H:%M:%S")

            print("<---hanld_date-->",hanld_date)
            #获取符合条件列表
            appro_file_list = [y for y,v in file_time_dict.items() if v <= hanld_date]
            logger.info("<---获取符合条件列表:{0}--->".format(appro_file_list))

            return appro_file_list
        else:
            logger.info("<---源路径下没有找到符合条件的文件-->")
            return []
    except Exception as e:
        Implement_Status_Task.objects.filter(id=key_id).update(task_status=3,task_desc='任务执行失败  详细请看日志')
        logger.info("<---异常信息:{}  行数:{}-->".format(e,e.__traceback__.tb_lineno))



#文件移动接口
def Backups_File(body,key_id):
    try:
        logger.info('<---文件移动接口 获取的参数:{0},状态表id{1}--->'.format(body,key_id))
        source_path = body.get('source_path','')
        backups_path = body.get('backups_path','')
        interval_date = body.get('interval_date',0)
        date_type = body.get('date_type',0)

        appro_file_list = Check_File(source_path,interval_date,date_type,key_id)
        if appro_file_list:
            #目的路径
            if os.path.isdir(backups_path) == False:
                os.makedirs(backups_path)

            #拼接目的路径
            backups_file_list = os.listdir(backups_path)
            backups_file_list_sq = {os.path.join(source_path,p):p for p in backups_file_list}
            logger.info('<---拼接为目的路径文件集合:{0} 如果为空证明目标目录下无文件--->'.format(backups_file_list_sq))

            for appro_file_one in appro_file_list:
                #判断文件是否存在
                if appro_file_one in backups_file_list_sq:
                    os.remove(os.path.join(backups_path,backups_file_list_sq[appro_file_one]))
                shutil.move(appro_file_one,backups_path)

            logger.info('<---文件移动完成--->')

    except Exception as e:
        Implement_Status_Task.objects.filter(id=key_id).update(task_status=3,task_desc='任务执行失败  详细请看日志')
        logger.info("<---异常信息:{}  行数:{}-->".format(e,e.__traceback__.tb_lineno))



# 获取远端符合条件的文件列表
def Long_Range_Check_File(ssh,source_path,interval_date,date_type,key_id=None):
    try:
        logger.info("<---获取远端符合条件的文件列表接口 连接信息:{0},源地址:{1},时间间隔:{2},时间类型:{3}--->".format(ssh,source_path,interval_date,date_type))
        #获取文件列表
        # body = json.loads(request.body.decode())
        # source_path = body.get('source_path','')
        # date_type = body.get('date_type','')
        # interval_date = body.get('interval_date','')

        p,result,f = ssh.exec_command("ls -rlt {0}".format(source_path))
        result_lis = result.readlines()
        logger.info("<---获取远端文件列表:{0}--->".format(result_lis))
        if result_lis:
            #只判断文件类型 获取符合条件的文件
            # file_sp = [a.split(' ') for a in result_lis[1:]]
            # 过滤文件夹
            file_info_name = [b[-1:][0].strip('\n') for b in [a.split(' ') for a in result_lis] if b[0][0]=='-']
            logger.info("<---过滤文件夹后的列表:{0}--->".format(file_info_name))
            #获取最后一次文件状态修改时间
            stat_info_dict = {}
            for file_stat in file_info_name:
                am,stat_result,co=ssh.exec_command("stat {0}/{1}".format(source_path,file_stat))
                stat_result_list = stat_result.readlines()
                logger.info("<--- 文件名:{0} 获取文件信息:{1}--->".format(file_stat,stat_result_list))
                stat_info_dict[file_stat] = '%s%s' % (stat_result_list[6].split(' ')[1],stat_result_list[6].split(' ')[2],)

            logger.info("<---获取最后一次文件状态修改时间:{0}--->".format(stat_info_dict))

            current_date = datetime.datetime.now()
            if date_type == 1:
                hanld_date = (current_date-relativedelta(months=int(interval_date))).strftime("%Y-%m-%d %H:%M:%S")
            else:
                hanld_date = (current_date-relativedelta(days=int(interval_date))).strftime("%Y-%m-%d %H:%M:%S")

            #获取符合条件列表
            # appro_file_list = ['{0}/{1}'.format(source_path,y) for y,v in stat_info_dict.items() if v >= hanld_date]
            appro_file_list = [y for y,v in stat_info_dict.items() if v <= hanld_date]
            logger.info("<---远端符合文件的列表:{0}--->".format(appro_file_list))
            return appro_file_list
        else:
            logger.info("<---路径下没有符合条件的数据文件--->")
            return []

    except Exception as e:
        logger.info("<---异常信息:{}  行数:{}-->".format(e,e.__traceback__.tb_lineno))
        Implement_Status_Task.objects.filter(id=key_id).update(task_status=3,task_desc='任务执行失败  详细请看日志')
    # finally:
    #     if ssh:
    #         ssh.close()



#文件上传
def Long_Range_Put_File(long_range_ip,long_range_user,long_range_pwd,backups_path,local_path,appro_file_list,key_id=None):
    try:
        logger.info("文件上传接口 参数:目标ip:{0},目标用户:{1},密码:{2},地址:{3},本地地址:{4},文件列表:{5}".
                format(long_range_ip,long_range_user,long_range_pwd,backups_path,local_path,appro_file_list))
        #获取ssh控制  sftp服务 和符合条件的文件列表
        ssh,sftp = Long_Rnge_SSH_Clint(long_range_ip,long_range_user,long_range_pwd)

        # appro_file_list = Long_Range_Check_File(ssh,source_path,interval_date,date_type)
        # print("<--appro--->",appro_file_list)
        #查看远端路径
        stdin,stdout,stderr = ssh.exec_command('find {0}'.format(backups_path))
        result = stdout.read().decode('utf-8')
        #远端路径不存在 就创建
        if len(result) == 0:
            ssh.exec_command('mkdir {0}'.format(backups_path))

        for appro_file_one in appro_file_list:
            sftp.put('{0}/{1}'.format(local_path,appro_file_one),'{0}/{1}'.format(backups_path,appro_file_one))
        logger.info("<---向远端上传文件完成-->")
    except Exception as e:
        logger.info("<---异常信息:{}  行数:{}-->".format(e,e.__traceback__.tb_lineno))
        Implement_Status_Task.objects.filter(id=key_id).update(task_status=3,task_desc='任务执行失败  详细请看日志')
        # data = {'code':2,'msg':"<---异常信息{}  行数{}-->".format(e,e.__traceback__.tb_lineno),'data':'Failure'}
        # return HttpResponse(json.dumps(data),content_type='application/json')
    finally:
        if ssh:
            ssh.close()

#文件传输
def Long_Range_Move_File(body,key_id):
    try:
        # body = json.loads(request.body.decode())
        # logger.info('<---向远端上传文件 获取的参数:{}--->'.format(body))
        source_ip = body.get('source_ip','')
        source_user = body.get('source_user','')
        source_pwd = body.get('source_pwd','')
        source_path = body.get('source_path','')
        interval_date = body.get('interval_date','')
        date_type = body.get('date_type','')
        long_range_ip = body.get('long_range_ip','')
        long_range_user = body.get('long_range_user','')
        long_range_pwd = body.get('long_range_pwd','')
        backups_path = body.get('backups_path','')
        local_path = body.get('local_path','')
        #获取ssh控制  sftp服务 和符合条件的文件列表
        ssh,sftp = Long_Rnge_SSH_Clint(source_ip,source_user,source_pwd)

        appro_file_list = Long_Range_Check_File(ssh,source_path,interval_date,date_type,key_id)
        if appro_file_list:
            for appro_file_one in appro_file_list:
                sftp.get('{0}/{1}'.format(source_path,appro_file_one),'{0}/{1}'.format(local_path,appro_file_one))

            logger.info("<------文件下载完成------>")

    except Exception as e:
        if ssh:
            ssh.close()
        Implement_Status_Task.objects.filter(id=key_id).update(task_status=3,task_desc='任务执行失败  详细请看日志')
        logger.info("<---异常信息:{}  行数:{}-->".format(e,e.__traceback__.tb_lineno))
    else:
        try:
            if ssh:
                ssh.close()
            if appro_file_list:
                Long_Range_Put_File(long_range_ip,long_range_user,long_range_pwd,backups_path,local_path,appro_file_list,key_id)
                logger.info("<------文件迁移完成------>")
                # data = {'code':1,'msg':"文件迁移完成",'data':'success'}
                # return HttpResponse(json.dumps(data),content_type='application/json')
        except Exception as e:
            logger.info("<------文件上传失败------>")
            Implement_Status_Task.objects.filter(id=key_id).update(task_status=3,task_desc='任务执行失败  详细请看日志')
    # finally:
    #     if ssh:
    #         ssh.close()

#向数据库中写入数据
def Long_Range_File_Implement(body,key_id):
    try:
        logger.info("<---数据库写入接口 参数:{0} 状态表id:{1}--->".format(body,key_id))
        db_tablename = body.get('db_tablename','')
        filepath = body.get('filepath','')
        #数据库连接
        conn = Databases_Conn(body)
        #获取备份的文件列表
        filepath_list = Databases_File_Write(db_tablename,filepath,conn,key_id)
        #获取ssh控制  sftp服务 和符合条件的文件列表
        # ssh,sftp = Long_Rnge_SSH_Clint(body)
        #
        # #查看远端路径
        # stdin,stdout,stderr = ssh.exec_command('find {0}'.format(backups_path))
        # result = stdout.read().decode('utf-8')
        # #远端路径不存在 就创建
        # if len(result) == 0:
        #     ssh.exec_command('mkdir {0}'.format(backups_path))
        #
        # for appro_file_one in filepath_list:
        #     file_path_ls = appro_file_one.split('/')
        #     sftp.put(appro_file_one,os.path.join(backups_path,file_path_ls[-1:][0]))

        #获取另一个数据连接
        database_dict_1 = {'db_ip':body.get('db_ip_lg',''),'db_username':body.get('db_username_lg',''),'db_password':body.get('db_password_lg',''),
                         'db_port':body.get('db_port_lg',''),'db_name':body.get('db_name_lg','')}

        conn_lg = Databases_Conn(database_dict_1)
        cursor_lg = conn_lg.cursor()

        #分批提交条数
        submit_num = 5000
        for appro_file_one_t in filepath_list:
            # with open(appro_file_one_t,'r+') as file_read:
            logger.info("<---开始读取数据库备份文件-->")
            file_read = open(appro_file_one_t,'r+',encoding='utf-8')
            #获取文件行数
            # count = 0
            # for index, line in enumerate(file_read):
            #     count += 1
            #分批页数
            # inbatches = math.ceil(count/submit_num)

            pl = 0
            pn = 1
            while True:
                pl+=1
                sql_str = file_read.readline().strip('\n')
                if sql_str:
                    print('sql_str',sql_str)
                    cursor_lg.execute(sql_str)
                    if pl >= submit_num * pn:
                        logger.info("<---提交插入事务第:{0}次 一次:{1}笔-->".format(pn,pl))
                        conn_lg.commit()
                        pn += 1
                else:
                    logger.info("<---提交插入事务第:{0}次 共提交:{1}笔-->".format(pn,pl-1))
                    conn_lg.commit()
                    break

        logger.info("<---数据迁移完成-->")
    except Exception as e:
        if conn:
            conn.close()
        if conn_lg:
            conn_lg.rollback()
            conn_lg.close()
        Implement_Status_Task.objects.filter(id=key_id).update(task_status=3,task_desc='任务执行失败  详细请看日志')
        logger.info("<---异常信息{}  行数{}-->".format(e,e.__traceback__.tb_lineno))
