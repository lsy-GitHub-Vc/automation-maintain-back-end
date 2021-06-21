#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#@time:
#@Author:lsy
#@file:
#@function:-----------

from Crypto.Cipher import AES
import base64
from automatization.settings import logger
import re

'''
python 在 Windows下使用AES时要安装的是pycryptodome 模块

python 在 Linux下使用AES时要安装的是pycrypto模块
'''


class AESEBC(object):

    def __init__(self):
        self.key = 'wG4@aA1@eB1$bC2!eE6#fE16cB4@dS=='
        self.model = AES.MODE_ECB
    '''
    采用AES EBC加密算法
    '''
    # str不是32的倍数那就补足为16的倍数
    def add_to_32(self,value):
        while len(value) % 32 != 0:
            value += '\0'
        return str.encode(value)  # 返回bytes

    #加密方法
    def Encrypt(self,pwd):
        logger.info('<---调用密码加密接口--->')
        try:
            # 初始化加密器
            aes = AES.new(self.add_to_32(self.key),self.model)
            #先进行aes加密
            encrypt_aes = aes.encrypt(self.add_to_32(pwd))
            #用base64转成字符串形式
            encrypted_key = str(base64.encodebytes(encrypt_aes), encoding='utf-8')  # 执行加密并转码返回bytes
            return encrypted_key
        except Exception as e:
            logger.info('<---密码加密异常 异常信息:{0} 异常行数:{1}--->'.format(e,e.__traceback__.tb_lineno))
    #解密方法
    def Decrypt(self,key):
        logger.info('<---调用密码解密接口--->')
        try:
            # 初始化加密器
            aes = AES.new(self.add_to_32(self.key),self.model)
            #优先逆向解密base64成bytes
            base64_decrypted = base64.decodebytes(key.encode(encoding='utf-8'))
            #执行解密密并转码返回str
            decrypted_pwd = str(aes.decrypt(base64_decrypted),encoding='utf-8').replace('\0','')
            return decrypted_pwd
        except Exception as e:
            logger.info('<---密码解密异常 异常信息:{0} 异常行数:{1}--->'.format(e,e.__traceback__.tb_lineno))





# class AESCBC:
#
#     '''
#     采用AES CBC加密算法
#     '''
#     def __init__(self):
#         self.key = 'wG4@aA1@eB1$bC2='.encode('utf-8')  # 定义key值
#         self.mode = AES.MODE_CBC
#         self.bs = 16  # block size
#         self.PADDING = lambda s: s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)
#
#     # 加密
#     def encrypt(self, text):
#         generator = AES.new(self.key, self.mode, self.key)  # 这里的key 和IV 一样 ，可以按照自己的值定义
#         crypt = generator.encrypt(self.PADDING(text).encode('utf-8'))
#         crypted_str = base64.b64encode(crypt)   #输出Base64
#         # crypted_str = binascii.b2a_hex(crypt)  # 输出Hex
#         result = crypted_str.decode()
#         return result
#
#     # 解密
#     def decrypt(self, text):
#         generator = AES.new(self.key, self.mode, self.key)
#         text += (len(text) % 4) * '='
#         decrpyt_bytes = base64.b64decode(text)           #输出Base64
#         # decrpyt_bytes = binascii.a2b_hex(text)  # 输出Hex
#         meg = generator.decrypt(decrpyt_bytes)
#         # 去除解码后的非法字符
#         try:
#             result = re.compile('[\\x00-\\x08\\x0b-\\x0c\\x0e-\\x1f\n\r\t]').sub('', meg.decode())
#         except Exception:
#             result = '解码失败，请重试!'
#         return result
#
# if __name__ == '__main__':
#
#     a = AESCBC()
#     print(a.encrypt('Root@123456'))
#     print(a.decrypt(a.encrypt('Root@123456')))
