from django.urls import path
from .views import *

app_name = 'adminpanel'

urlpatterns = [
    path('admin', AdminView.as_view(), name='admin_main'),
    path('admin/register', AdminFirstRegisterView.as_view(), name='admin_register'),
]