#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#@time:
#@Author:lsy
#@file:
#@function:-----------

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#@time:
#@Author:lsy
#@file:
#@function:-----------

from  django.db import models

class Databases_Migration_Task(models.Model):
    id = models.AutoField(primary_key=True)#主键
    task_id = models.CharField('任务id',max_length=100,null=True,blank=True)
    task_type = models.IntegerField('任务类型',null=True,blank=True)
    create_time = models.DateTimeField('创建日期',auto_now_add=True,null=True,blank=True)
    db_ip = models.CharField('源数据库地址ip',max_length=100,null=True,blank=True)
    db_username = models.CharField('源数据库用户名',max_length=255,null=True,blank=True)
    db_password = models.CharField('源数据库用户密码',max_length=255,null=True,blank=True)
    db_port = models.IntegerField('源数据库端口',null=True,blank=True)
    db_name = models.CharField('源数据库库名',max_length=255,null=True,blank=True)
    db_tablename = models.TextField('数据库需要操作的列表',null=True,blank=True)
    filepath = models.CharField('生成文件的地址',max_length=255,null=True,blank=True)
    db_ip_lg = models.CharField('目标数据库ip',max_length=255,null=True,blank=True)
    db_username_lg = models.CharField('目标数据库用户',max_length=255,null=True,blank=True)
    db_password_lg = models.CharField('目标数据库用户密码',max_length=255,null=True,blank=True)
    db_port_lg = models.IntegerField('目标数据库端口',null=True,blank=True)
    db_name_lg = models.CharField('目标数据库库名',max_length=255,null=True,blank=True)

    class Meta:
        verbose_name = '数据迁移任务表'
        verbose_name_plural = verbose_name
        db_table = 'data_migration_task'

class File_Migration_Task(models.Model):
    id = models.AutoField(primary_key=True)#主键
    task_id = models.CharField('任务id',max_length=100,null=True,blank=True)
    task_type = models.IntegerField('任务类型',null=True,blank=True)
    create_time = models.DateTimeField('创建日期',auto_now_add=True,null=True,blank=True)
    source_ip = models.CharField('源服务器ip',max_length=255,null=True,blank=True)
    source_user = models.CharField('源服务器用户名',max_length=255,null=True,blank=True)
    source_pwd = models.CharField('源服务器用户密码',max_length=255,null=True,blank=True)
    source_path = models.CharField('源服务器文件地址',max_length=255,null=True,blank=True)
    local_path = models.CharField('本地中转地址',max_length=255,null=True,blank=True)
    interval_date = models.CharField('时间间隔',max_length=255,null=True,blank=True)
    date_type = models.CharField('时间类型 1:月份 2:天数',max_length=255,null=True,blank=True)
    long_range_ip = models.CharField('目标服务器ip',max_length=100,null=True,blank=True)
    long_range_user = models.CharField('目标服务器用户',max_length=255,null=True,blank=True)
    long_range_pwd = models.CharField('目标服务器用户密码',max_length=255,null=True,blank=True)
    backups_path = models.CharField('目标服务器备份文件存放地址',max_length=255,null=True,blank=True)

    class Meta:
        verbose_name = '文件迁移任务表'
        verbose_name_plural = verbose_name
        db_table = 'file_migration_task'

class Implement_Status_Task(models.Model):
    id = models.AutoField(primary_key=True)#主键
    task_id = models.CharField('迁移任务id',max_length=100,null=True,blank=True)
    create_time = models.DateTimeField('创建日期',auto_now_add=True,null=True,blank=True)
    task_imp_operation = models.IntegerField('任务操作类型 1:时间间隔 2:时间点 3:corn',null=True,blank=True)
    task_imp_interval = models.IntegerField('时间间隔类型 0:不启用该间隔 1:秒 2:分 3:小时',null=True,blank=True)
    task_imp_time = models.CharField('具体的间隔数或时间点',max_length=255,null=True,blank=True)
    task_type = models.IntegerField("操作类型 1:数据库 2:文件",null=True,blank=True)
    task_status = models.IntegerField('执行状态',null=True,blank=True) #0:待执行  1:执行中 2:执行成功 3:执行失败
    task_desc = models.CharField('中文说明',max_length=255,null=True,blank=True)

    class Meta:
        verbose_name = '任务执行状态表'
        verbose_name_plural = verbose_name
        db_table = 'implement_status_task'
