from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
import uuid

from django.views.generic import ListView, DetailView, View
from .models import Course, Lecture, Wishes, Student


def add_to_wishlist(request, course_slug):
    course_queue = Course.objects.filter(slug=course_slug)
    if course_queue.exists():
        course = course_queue.first()
    else:
        return

    # WILL BE CHANGED TO CURRENT USER
    s = Student.objects.filter(username="user2").first()

    if not Wishes.objects.filter(user=s, cno=course):
        Wishes.objects.create(wishes_id=uuid.uuid1(), cno=course, user=s)
    else:
        Wishes.objects.filter(cno=course, user=s).delete()
    return redirect("courses:wishlist_items")
    #return render(request, 'main/wishlist.html')

class WishlistView(ListView):
    def get(self, request):
        # WILL BE CHANGED TO CURRENT USER
        s = Student.objects.filter(username="user2").first()
        wishlist_q = Wishes.objects.filter(user=s)
        context = {
            'wishlist_q': wishlist_q
        }
        return render(request, 'main/wishlist.html', context)


class CourseListView(ListView):
    model = Course

class CourseDetailView(DetailView):
    model = Course

class LectureView(View):
    # model = Lecture

    def get(self, request, course_slug, lecture_slug, *args, **kwargs):
        course_queue = Course.objects.filter(slug=course_slug)
        if course_queue.exists():
            course = course_queue.first()

        lecture_q = Lecture.objects.filter(lecture_slug=lecture_slug)
        if lecture_q.exists():
            lecture = lecture_q.first()

        context = {
            'object': lecture
        }

        return render(request, 'main/lecture_detail.html', context)

# Create your views here.
def index(request):
    return HttpResponse("MAYACAT")
