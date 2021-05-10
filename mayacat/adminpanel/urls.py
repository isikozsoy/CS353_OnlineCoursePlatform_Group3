from django.urls import path
from .views import *

app_name = 'courses'

urlpatterns = [
    path('admin', AdminView.as_view(), name='admin_main'),
    path('admin/login', AdminFirstRegisterView.as_view(), name='admin_register'),
]