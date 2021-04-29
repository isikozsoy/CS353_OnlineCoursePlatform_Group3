from django.urls import path

from .views import CourseListView, CourseDetailView, LectureView, course_detail

app_name = 'courses'

urlpatterns = [
    path('', CourseListView.as_view(), name='list'),
    path('<slug>', CourseDetailView.as_view(), name='desc'),
    path('<course_slug>/<lecture_slug>', LectureView.as_view(), name='lecture-detail'),
    path('<course_slug>', course_detail, name = 'course-detail'),
    path('wishlist/add_to_wishlist/<course_slug>', add_to_wishlist, name='user_wishlist'),
    path('cart', shopping_cart, name = 'cart'),
    path('<course_slug>/<lecture_slug>', LectureView.as_view(), name='lecture-detail'),
    path('checkout', checkout, name = 'checkout')
]