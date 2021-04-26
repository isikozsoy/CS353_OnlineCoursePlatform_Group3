from django.urls import path

from . import views
from .views import CourseListView, CourseDetailView, LectureView, WishlistView

app_name = 'courses'

urlpatterns = [
    path('', CourseListView.as_view(), name='list'),
    path('wishlist', WishlistView.as_view(), name='wishlist_items'),
    path('wishlist/add_to_wishlist/<course_slug>', views.add_to_wishlist, name='user_wishlist'),
    path('<slug>', CourseDetailView.as_view(), name='desc'),
    path('<course_slug>/<lecture_slug>', LectureView.as_view(), name='lecture-detail')
]