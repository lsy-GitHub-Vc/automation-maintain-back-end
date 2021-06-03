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
    hostaddress = models.CharField('主机地址',max_length=255,null=True,blank=True)
    hostport = models.IntegerField('主机端口',null=True,blank=True)
    visitproof = models.CharField('访问凭证',max_length=255,null=True,blank=True)
    describe = models.CharField('描述信息',max_length=255,null=True,blank=True)
    hoststatus = models.IntegerField('主机状态',null=True,blank=True)

    class Meta:
        verbose_name = '主机管理模型'
        verbose_name_plural = verbose_name
        db_table = 'host_info_manage'