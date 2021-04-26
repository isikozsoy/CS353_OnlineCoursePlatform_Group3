from django.shortcuts import render
from django.http import HttpResponse

from django.views.generic import ListView, DetailView, View
from .models import Course, Lecture, Announcement, Takes_note, Post, Quest_answ

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
            print(course)

        lecture_q = Lecture.objects.filter(lecture_slug=lecture_slug)
        if lecture_q.exists():
            lecture = lecture_q.first()

        lectures = Lecture.objects.filter(cno_id=course.cno)

        announcements = Announcement.objects.filter( cno_id = course.cno )

        notes = Takes_note.objects.filter( lecture_no_id = lecture.lecture_no ) #student will be added

        lecturecnt = lectures.count()

       # questions = Post.objects.raw('''SELECT postno
       #                                 FROM Post
       #                                 WHERE postno NOT IN (SELECT answer_no_id AS postno FROM Quest_answ ); ''')

        #qanda = Quest_answ.objects.all()


        context = {
            'curlecture': lecture,
            'course' : course,
            'lectures' : lectures,
            'announcements' : announcements,
            'notes' : notes,
            'lecturecnt' : lecturecnt
            #'questions' : questions
        }

        return render(request, 'main/lecture_detail.html', context)

# Create your views here.
def index(request):
    return HttpResponse("MAYACAT")
