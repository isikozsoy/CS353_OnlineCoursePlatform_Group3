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
        # THE COURSES WILL BE CHANGED AS TOP 5 MOST POPULAR AND TOP 5 HIGHEST RATED
        courses = Course.objects.raw('select * '
                                     'from courses_course;')

        topics = Topic.objects.raw('select * from main_topic order by topicname;')

        return render(request, 'main/main.html', {'object_list': courses,
                                                  'topic_list':topics})


