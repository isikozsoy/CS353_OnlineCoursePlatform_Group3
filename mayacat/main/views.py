
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
import uuid

from django.views.generic import ListView, DetailView, View
from .models import *
from accounts.models import *


class WishlistView(ListView):
    def get(self, request):
        # WILL BE CHANGED TO CURRENT USER
        s = request.user
        wishlist_q = Wishes.objects.filter(user=s)
        context = {
            'wishlist_q': wishlist_q
        }
        return render(request, 'main/wishlist.html', context)


def add_to_wishlist(request, course_slug):
    course_queue = Course.objects.filter(slug=course_slug)
    if course_queue.exists():
        course = course_queue.first()
    else:
        return

    # WILL BE CHANGED TO CURRENT USER
    s = request.user

    if not Wishes.objects.filter(user=s, cno=course):
        Wishes.objects.create(wishes_id=uuid.uuid1(), cno=course, user=s)
    else:
        Wishes.objects.filter(cno=course, user=s).delete()
    return redirect("courses:wishlist_items")


class MainView(View):
    def get(self, request):
        return render(request, 'main/main.html')


# Create your views here.
def index(request):
    return HttpResponse("MAYACAT")



def course_detail(request, course_id):
    course = Course.objects.raw('SELECT * FROM courses_course WHERE course_id = %s', [course_id])
    # WILL BE CHANGED TO CURRENT USER ?
    user_id = request.user.id
    registered = Enroll.objects.raw('SELECT enroll_id FROM X WHERE user = %s AND cno = %s', [user_id], [course_id])

    lecture_count = Lecture.objects.filter(cno_id=course.cno).count()

    rating = Rate.objects.raw('SELECT AVG(score) FROM X WHERE cno = %s', [course_id])
    advertisement = Advertisement.objects.raw('SELECT advertisement FROM X WHERE cno = %s', [course_id])

    comments = Finishes.objects.raw('SELECT comment FROM X WHERE cno = %s', [course_id])

    return render(request, 'main/course_detail.html', {'course': course, 'registered': registered,
                                                           'lecture_count': lecture_count, 'rating': rating,
                                                           'advertisement': advertisement, 'comments': comments})


def shopping_cart(request):

    # WILL BE CHANGED TO CURRENT USER ?
    user = request.user

    items_on_cart = Inside_Cart.objects.raw('SELECT * FROM X WHERE username = %s', [user.name]).all()

    items = Course.objects.raw('SELECT * FROM X WHERE cno = %s', [items_on_cart.cno])

    count = Inside_Cart.objects.filter(username = user.name).count()

    total_price = Course.objects.raw('SELECT SUM(price) FROM items')

    return render(request, 'main/shopping_cart.html', {'items': items, 'items_on_cart': items_on_cart,
                                                           'count': count, 'total_price': total_price})

def checkout(self):
    return render(request, 'main/checkout.html', {})
