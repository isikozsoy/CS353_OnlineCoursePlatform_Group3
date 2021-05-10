from django.urls import path
from .views import *

app_name = 'adminpanel'

urlpatterns = [
    path('admin', AdminView.as_view(), name='admin_main'),
    path('admin/register', AdminFirstRegisterView.as_view(), name='admin_register'),
    path('admin/save_course', save_courses, name='admin_save_course'),
    path('admin/create_lecture', save_courses, name='admin_create_lecture'),
]