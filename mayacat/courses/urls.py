from django.urls import path
from .views import *
from main.views import MainView

app_name = 'courses'

urlpatterns = [
    path('list', MainView.as_view(), name='list'),  # we can delete this one
    path('my_courses', MyCoursesView.as_view(), name='my_courses'),
    path('my_courses/add/<course_slug>', add_to_my_courses, name='user_mycourses'),
    path('<slug>', CourseDetailView.as_view(), name='desc'),
    path('<course_slug>/<lecture_slug>', LectureView.as_view(), name='lecture_detail'),
    #path('<course_slug>/<lecture_slug>', LectureView.as_view(), name='lecture_detail'),
    path('<course_slug>/<lecture_slug>/finish', CourseFinishView.as_view(), name='course_finish'),
]