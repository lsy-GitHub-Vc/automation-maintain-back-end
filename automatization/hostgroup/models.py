#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#@time:
#@Author:lsy
#@file:
#@function:-----------

from  django.db import models

class HostInfoManage(models.Model):
    id = models.AutoField(primary_key=True)#主键
    hostname = models.CharField('主机名称',max_length=255,null=True,blank=True)
    hostgroup = models.CharField('主机组',max_length=255,null=True,blank=True)
    hostip = models.CharField('主机地址',max_length=255,null=True,blank=True)
    port = models.IntegerField('主机端口',null=True,blank=True)
    credential = models.CharField('访问凭证',max_length=255,null=True,blank=True)
    description = models.CharField('描述信息',max_length=255,null=True,blank=True)
    hoststatus = models.IntegerField('主机状态',null=True,blank=True)

    class Meta:
        verbose_name = '主机管理模型'
        verbose_name_plural = verbose_name
        db_table = 'host_info_manage'

#主机用户管理
class UserManage(models.Model):
    id = models.AutoField(primary_key=True)#主键
    name = models.CharField('访问凭证',max_length=255,null=True,blank=True)
    username = models.CharField('用于ssh的用户名',max_length=255,null=True,blank=True)
    password = models.CharField('用于ssh的密码',max_length=255,null=True,blank=True)
    become_method = models.CharField('当需要特权时是su或者enable',max_length=255,null=True,blank=True)
    become_user = models.CharField('当需要特权时 使用的用户名',max_length=255,null=True,blank=True)
    become_password = models.CharField('当需要特权时 使用的密码',max_length=255,null=True,blank=True)
    public_key = models.TextField('公钥认证',null=True,blank=True)

    class Meta:
        verbose_name = '主机用户管理模型'
        verbose_name_plural = verbose_name
        db_table = 'host_user_manage'