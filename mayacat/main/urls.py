from django.urls import path

from .views import *

app_name = 'main'

urlpatterns = [

    path('', CourseListView.as_view(), name='list'),
    path('cart', ShoppingCartView.as_view(), name='cart'),
    path('checkout', ShoppingCheckoutView.as_view(), name='checkout'),
    path('<slug>', CourseDetailView.as_view(), name='desc'),
    path('<course_slug>/<lecture_slug>', LectureView.as_view(), name='lecture-detail'),
    path('<course_slug>', course_detail, name='course-detail'),
    path('wishlist/add_to_wishlist/<course_slug>', add_to_wishlist, name='user_wishlist'),
    path('<course_slug>/<lecture_slug>', LectureView.as_view(), name='lecture-detail'),
]
