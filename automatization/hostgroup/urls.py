"""automatization URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include

from automatization.hostgroup.views import Ins_HostInfo,Bulk_Create_HostInfo,Sel_HostInfo,Del_HostInfo,Upd_HostInfo,Ins_UserManage,Del_UserManage,Upd_UserManage,\
    Sel_UserManage,Generate_DB_Excel,Single_Connect_Check

urlpatterns = [

    # path('admin/', admin.site.urls),
    path('ins_hostinfo',Ins_HostInfo), #主机信息添加
    path('bulk_create_hostinfo',Bulk_Create_HostInfo),#批量主机信息添加
    path('single_connect_check',Single_Connect_Check),#单笔校验主机连通性
    path('sel_hostinfo',Sel_HostInfo),#主机信息查询
    path('upd_hostinfo',Upd_HostInfo),#主机信息修改
    path('del_hostinfo',Del_HostInfo),#主机信息删除
    path('ins_usermanage',Ins_UserManage),#主机用户信息添加
    path('del_usermanage',Del_UserManage),#主机用户信息删除
    path('upd_usermanage',Upd_UserManage),#主机用户信息修改
    path('sel_usermanage',Sel_UserManage),#主机用户信息查询
    path('generate_db_excel',Generate_DB_Excel),#生成主机表的excel文件


]
