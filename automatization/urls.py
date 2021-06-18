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
# from automatization.hostgroup.views import Ins_HostInfo,Bulk_Create_HostInfo,Sel_HostInfo,Del_HostInfo,Upd_HostInfo,Bulk_Delete_HostInfo

from automatization.data_migration.views import Databases_Generate_File,Backups_File,Long_Range_Move_File,Long_Range_File_Implement,\
    Long_Range_Check_File

from automatization.data_migration.databases_operation import Ins_Databases_Migration_Task,Del_Databases_Migration_Task,Upd_Databases_Migration_Task,\
    Sel_Databases_Migration_Task,Sel_Implement_Status_Task,Ins_File_Migration_Task,Del_File_Migration_Task,Upd_File_Migration_Task,Sel_File_Migration_Task

from automatization.data_migration.apscheduler_task import Upd_Implement_Status_Task

urlpatterns = [
    path('admin/', admin.site.urls),
    path('data_migration/',include('automatization.data_migration.urls')),
    path('hostgroup/',include('automatization.hostgroup.urls')),
]
