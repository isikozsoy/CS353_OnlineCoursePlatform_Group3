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
    path('wishlist', WishlistView.as_view(), name='wishlist_items'),
    path('cart/trash/<inside_cart_id>', TrashView.as_view(), name='add_trash_btn'),
    path('topic/<topicname>', topic_course_listing_page, name='topic_course_list'),
    path('notifications', NotificationView.as_view(), name='notifications'),
    path('checkout', ShoppingCheckoutView.as_view(), name='checkout'),
    path('ad_offers', AdOffersView.as_view(), name='ad_offers'),
    path('ad_offers/accept_ad/<ad_no>', accept_ad, name='accept_ad'),
    path('ad_offers/refuse_ad/<ad_no>', refuse_ad, name='refuse_ad'),
    path('taught_courses', TaughtCoursesView.as_view(), name='taught_courses'),
    path('cart/gift/<course_slug>', AddAsGift.as_view(), name='cart_gift'),
    path('discounts', DiscountsView.as_view(), name='discounts'),
    path('discounts/<offer_no>', JoinCoursesView.as_view(), name='discount_courses'),

]
