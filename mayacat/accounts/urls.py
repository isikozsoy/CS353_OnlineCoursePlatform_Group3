from django.urls import re_path, path
from .views import *

app_name = 'accounts'

urlpatterns = [
    re_path(r'^register*', RegisterView.as_view()),
    path('login', LoginView.as_view()),
    path('logout', LogoutView.as_view(), name='logout'),
]