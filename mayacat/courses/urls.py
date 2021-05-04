from django.urls import path
from .views import *
from main.views import MainView
from courses.views import AddComplainView

app_name = 'courses'

urlpatterns = [
    path('list', MainView.as_view(), name='list'),  # we can delete this one
    path('add', AddCourseView.as_view(), name='add_course'),
    path('add/<course_slug>', AddLectureToCourseView.as_view(), name='add_lecture'),
    path('my_courses', MyCoursesView.as_view(), name='my_courses'),
    path('my_courses/add/<course_slug>', add_to_my_courses, name='user_mycourses'),
    path('<course_slug>/complain', AddComplainView.as_view(), name='complaint'),
    path('<course_slug>/refund', RefundRequestView.as_view(), name='refund'),
    path('<course_slug>', CourseDetailView.as_view(), name='desc'),
    path('offer_ad/<course_slug>', OfferAdView.as_view(), name='offer_ad'),
    path('<course_slug>/<lecture_slug>', LectureView.as_view(), name='lecture_detail')
]
