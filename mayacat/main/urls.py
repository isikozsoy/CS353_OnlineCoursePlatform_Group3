from django.urls import path

from .views import *

app_name = 'main'

urlpatterns = [
    path('', MainView.as_view()),
    path('wishlist', WishlistView.as_view(), name='wishlist_items'),
    path('wishlist/add_to_wishlist/<course_slug>', add_to_wishlist, name='user_wishlist'),
]