#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#@time:
#@Author:lsy
#@file:
#@function:-----------

from .views import *
from threading import Thread
from automatization.settings import logger
from concurrent.futures import ThreadPoolExecutor,as_completed
from .models import HostInfoManage


# 定义一个装饰器（定义一个非阻塞的模式）
def Tr_async(fun):
    def wrapper(*args,**kwargs):
        thr = Thread(target=fun,args=args,kwargs=kwargs)
        thr.start()
    return wrapper

#定义一个线程池方法
@Tr_async
def Tread_pool(fun,tasks):
    logger.info('<---调用创建线程池接口--->')
    try:
        '''
            这个还是不要复用了 多个线程池对象 去操作结果变量 还是有可能出现结果变量丢失的 而且重要的是上一个调用对象没执行完 线程没释放
            后面的只有等着 影响效率
        '''
        with ThreadPoolExecutor() as pool:
            # results = pool.map(fun,tasks)
            results = [pool.submit(fun,tk) for tk in tasks]
        # result_thr = [rt for rt in results]
        result_thr = [rt.result() for rt in as_completed(results)]

        logger.info('<---主机连通性测试  线程池返回结果集:{0}--->'.format(result_thr))
        #判断业务场景
        # if fun is Clint_Host_Test:
        logger.info('<---线程池(业务场景)  主机连通性测试--->')
        #更新数据库状态
        #获取连接状态为0的凭证id
        client_socket_fail = [a[0] for a in result_thr if a != None and a[1]==0]
        logger.info('<---获取的socket连接失败的凭证id:{0}--->'.format(client_socket_fail))
        #获取连接状态为1的凭证id
        client_ssh_fai = [b[0] for b in result_thr if b != None and b[1]==1]
        logger.info('<---获取socket连接成功 的SSH连接失败的凭证id:{0}--->'.format(client_ssh_fai))
        #获取连接状态为2的凭证id
        client_ssh_suc = [c[0] for c in result_thr if c != None and c[1]==2]
        logger.info('<---获取的SSH连接成功的凭证id:{0}--->'.format(client_ssh_suc))
        #获取异常的数据
        #判断是否有异常数据
        except_credential = []
        if len(tasks) > (len(client_socket_fail)+len(client_ssh_fai)+len(client_ssh_suc)):
            #获取总的凭证id
            all_credential = [d['credential'] for d in tasks]
            #获取不在上述三种状态的id
            all_client_crede = client_socket_fail + client_ssh_fai + client_ssh_suc
            except_credential = [e for e in all_credential if e not in all_client_crede]
            logger.info('<---获取异常的凭证id:{0}--->'.format(except_credential))

        if client_socket_fail:
            HostInfoManage.objects.filter(credential__in = client_socket_fail).update(hoststatus = 0)
            logger.info('<---更新socket连接失败的数据库状态--->'.format(client_socket_fail))

        if client_ssh_fai:
            HostInfoManage.objects.filter(credential__in = client_ssh_fai).update(hoststatus = 1)
            logger.info('<---更新socket连接成功 SSH连接失败的数据库状态--->'.format(client_ssh_fai))

        if client_ssh_suc:
            HostInfoManage.objects.filter(credential__in = client_ssh_suc).update(hoststatus = 2)
            logger.info('<---更新SSH连接成功的数据库状态--->'.format(client_ssh_suc))

        if except_credential:
            HostInfoManage.objects.filter(credential__in = except_credential).update(hoststatus = 3)
            logger.info('<---更新连接异常的数据库状态--->'.format(except_credential))

    except Exception as e:
        logger.info('<---线程池初始化失败 异常信息:{0} 异常行数:{1}--->'.format(e,e.__traceback__.tb_lineno),)
