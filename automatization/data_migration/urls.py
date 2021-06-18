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
from django.urls import path
# from automatization.data_migration.views import Databases_Generate_File,Backups_File,Long_Range_Move_File,Long_Range_File_Implement,\
#     Long_Range_Check_File

from automatization.data_migration.databases_operation import Ins_Databases_Migration_Task,Del_Databases_Migration_Task,Upd_Databases_Migration_Task,\
    Sel_Databases_Migration_Task,Sel_Implement_Status_Task,Ins_File_Migration_Task,Del_File_Migration_Task,Upd_File_Migration_Task,Sel_File_Migration_Task

from automatization.data_migration.apscheduler_task import Upd_Implement_Status_Task



urlpatterns = [
    # path('admin/', admin.site.urls),
    # path('databases_generate_file',Databases_Generate_File),#生成数据库文件
    # path('backups_file',Backups_File),
    # path('long_range_move_file',Long_Range_Move_File),#文件上传
    # path('long_range_file_implement',Long_Range_File_Implement),#远程数据同步


    path('ins_databases_migration_task',Ins_Databases_Migration_Task), #添加数据库迁移信息
    path('del_databases_migration_task',Del_Databases_Migration_Task),#删除....
    path('upd_databases_migration_task',Upd_Databases_Migration_Task),#修改...
    path('sel_databases_migration_task',Sel_Databases_Migration_Task),#查询...
    path('sel_implement_status_task',Sel_Implement_Status_Task), #查询历史任务信息
    path('upd_implement_status_task',Upd_Implement_Status_Task),#执行任务
    path('ins_file_migration_task',Ins_File_Migration_Task),#添加文件迁移信息
    path('del_file_migration_task',Del_File_Migration_Task),#删除...
    path('upd_file_migration_task',Upd_File_Migration_Task),#修改...
    path('sel_file_migration_task',Sel_File_Migration_Task),#查询...


]
