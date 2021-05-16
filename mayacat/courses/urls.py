from django.conf.urls import url
from django.urls import path, re_path
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
    path('<course_slug>/edit', ChangeCourseSettingsView.as_view(), name='course_edit'),
    path('<course_slug>/deletecontributor/<c_username>', DeleteContributerView.as_view(),name = 'delete_contributor'),
    path('<course_slug>/complain', AddComplainView.as_view(), name='complaint'),
    path('<course_slug>/refund', RefundRequestView.as_view(), name='refund'),
    path('<course_slug>/mark_as_complete', mark_as_complete, name='mark_as_complete'),
    path('<course_slug>/', CourseDetailView.as_view(), name='desc'),
    path('<course_slug>', CourseDetailView.as_view(), name='desc'),
    path('add_gift_to_cart/<course_slug>', add_gift_to_cart, name='add_gift_to_cart'),
    path('offer_ad/<course_slug>', OfferAdView.as_view(), name='offer_ad'),
    path('<course_slug>/finish', CourseFinishView.as_view(), name='course_finish'),
    path('<course_slug>/certificate', CourseCertificateView.as_view(), name='course_certificate'),
    path('<course_slug>/<lecture_slug>', LectureView.as_view(), name='lecture_detail'),
    path('<course_slug>/<lecture_slug>/answer/<question_no>', AddAnswerView.as_view(),name = 'add_answer'),
    path('<course_slug>/<lecture_slug>/deleteteacher/<t_username>', DeleteTeacherView.as_view(),name = 'delete_teacher'),
    path('<course_slug>/<lecture_slug>/deletenote/<note_id>', DeleteNoteView.as_view(),name = 'delete_note'),
    path('<course_slug>/<lecture_slug>/deletequestion/<q_id>', DeleteQuestionView.as_view(),name = 'delete_question'),
    path('<course_slug>/<lecture_slug>/deleteanswer/<a_id>', DeleteAnswerView.as_view(),name = 'delete_answer'),
    path('<course_slug>/<lecture_slug>/deleteannouncement/<ann_id>', DeleteAnnouncementView.as_view(),name = 'delete_announcement'),
    path('<course_slug>/<lecture_slug>/deleteassignment/<a_id>', DeleteAssignmentView.as_view(),name = 'delete_assignment'),
    path('<course_slug>/<lecture_slug>/deletelecturematerial/<lm_id>', DeleteLectureMaterialView.as_view(),name = 'delete_lecturematerial'),

]
