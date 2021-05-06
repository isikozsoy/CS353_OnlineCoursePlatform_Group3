from django.urls import path

from .views import *

app_name = 'main'

urlpatterns = [

    path('', MainView.as_view()),
    #path('', CourseListView.as_view(), name='list'),
    path('cart', ShoppingCartView.as_view(), name='cart'),
    path('checkout', ShoppingCheckoutView.as_view(), name='checkout'),
    path('<course_slug>', course_detail, name='course-detail'),
]
