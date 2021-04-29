from django.urls import path

from .views import CourseListView, CourseDetailView, LectureView, course_detail

app_name = 'courses'

urlpatterns = [
    path('', CourseListView.as_view(), name='list'),
    path('<slug>', CourseDetailView.as_view(), name='desc'),
    path('<course_slug>/<lecture_slug>', LectureView.as_view(), name='lecture-detail'),
    path('<course_slug>', course_detail, name='course-detail')
]