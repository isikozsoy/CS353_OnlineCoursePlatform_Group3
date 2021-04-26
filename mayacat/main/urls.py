from django.urls import path

from .views import *

app_name = 'courses'

urlpatterns = [
    path('', MainView.as_view()),
    path('list', CourseListView.as_view(), name='list'),
    path('', CourseListView.as_view(), name='list'),
    path('wishlist', WishlistView.as_view(), name='wishlist_items'),
    path('wishlist/add_to_wishlist/<course_slug>', views.add_to_wishlist, name='user_wishlist'),
    path('my_courses', MyCoursesView.as_view(), name='my_courses'),
    path('my_courses/add/<course_slug>', views.add_to_my_courses, name='user_mycourses'),
    path('<slug>', CourseDetailView.as_view(), name='desc'),
    path('<course_slug>/<lecture_slug>', LectureView.as_view(), name='lecture-detail')
]