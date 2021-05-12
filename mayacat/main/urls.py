from django.urls import path

from .views import *
from courses.views import *

app_name = 'main'

urlpatterns = [
    path('', MainView.as_view(), name='list'),
    path('cart', ShoppingCartView.as_view(), name='cart'),
    path('cart/remove/<item_id>', remove_from_cart, 'remove_from_cart'),
    path('checkout', ShoppingCheckoutView.as_view(), name='checkout'),
    path('wishlist', WishlistView.as_view(), name='wishlist_items'),
    path('offers', OffersView.as_view(), name='offers'),
    path('wishlist/add_to_wishlist/<course_slug>', add_to_wishlist, name='user_wishlist'),
    path('notifications', NotificationView.as_view(), name='notifications'),
    path('checkout', ShoppingCheckoutView.as_view(), name='checkout'),
    path('ad_offers', AdOffersView.as_view(), name='ad_offers'),
    path('ad_offers/accept_ad/<ad_no>', accept_ad, name='accept_ad'),
    path('ad_offers/refuse_ad/<ad_no>', refuse_ad, name='refuse_ad'),
    path('taught_courses', TaughtCoursesView.as_view(), name='taught_courses')
]
