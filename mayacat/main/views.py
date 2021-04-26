from django.shortcuts import render
from django.http import HttpResponse

from django.views.generic import ListView, DetailView, View
from .models import Course, Lecture

class MainView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return render(request, 'main/course_list.html')
        return render(request, 'main/main.html')

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
