from django.urls import path

from .views import *
from courses.views import *

app_name = 'main'

urlpatterns = [
    path('', MainView.as_view(), name='list'),
    path('cart', ShoppingCartView.as_view(), name='cart'),
    path('checkout', ShoppingCheckoutView.as_view(), name='checkout'),
    path('wishlist', WishlistView.as_view(), name='wishlist_items'),
    path('offers', OffersView.as_view(), name='offers'),
    path('wishlist/add_to_wishlist/<course_slug>', add_to_wishlist, name='user_wishlist'),
    path('notifications', NotificationView.as_view(), name='notifications')
]
