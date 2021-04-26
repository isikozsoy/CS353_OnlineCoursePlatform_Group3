from django.urls import path
from .views import *

app_name = 'accounts'

urlpatterns = [
    path('register/instructor', RegisterInstructorView.as_view()),
    path('register', RegisterView.as_view()),
    path('register/', RegisterView.as_view()),
    path('login', LoginView.as_view()),
]