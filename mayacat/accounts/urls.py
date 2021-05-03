from django.urls import re_path, path
from .views import *

app_name = 'accounts'

urlpatterns = [
    path('register', RegisterView.as_view()),
    path('register/instructor', RegisterView.as_view()),
    path('register/advertiser', RegisterView.as_view()),
    path('login', LoginView.as_view()),
    path('logout', LogoutView.as_view(), name='logout'),
    path('account', AccountView.as_view(), name='account'),
#    path('account-change', AccountView.as_view(), name='account-change'),
#    path('<username>', AnotherAccountView.as_view(), name='user_account'),
]