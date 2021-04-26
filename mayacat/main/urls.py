from django.urls import path

from .views import *

app_name = 'courses'

urlpatterns = [
    path('', MainView.as_view()),
    path('list', CourseListView.as_view(), name='list'),
    path('<slug>', CourseDetailView.as_view(), name='desc'),
    path('<course_slug>/<lecture_slug>', LectureView.as_view(), name='lecture-detail')
]