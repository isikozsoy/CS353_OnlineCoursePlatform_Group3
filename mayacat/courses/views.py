from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import ListView, DetailView, View
from main.models import *
from .models import *


class MyCoursesView(ListView):
    def get(self, request):
        # WILL BE CHANGED TO CURRENT USER
        s = request.user
        my_courses_q = Enroll.objects.filter(user=s)
        context = {
            'my_courses_q': my_courses_q
        }
        return render(request, 'main/my_courses.html', context)


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

        announcements = Announcement.objects.filter(cno_id=course.cno)

        notes = Takes_note.objects.filter(lecture_no_id=lecture.lecture_no)  # student will be added

        lecturecnt = lectures.count()

        # questions = Post.objects.raw('''SELECT postno
        #                                 FROM Post
        #                                 WHERE postno NOT IN (SELECT answer_no_id AS postno FROM Quest_answ ); ''')

        # qanda = Quest_answ.objects.all()

        context = {
            'curlecture': lecture,
            'course': course,
            'lectures': lectures,
            'announcements': announcements,
            'notes': notes,
            'lecturecnt': lecturecnt
            # 'questions' : questions
        }

        return render(request, 'main/lecture_detail.html', context)


def add_to_my_courses(request, course_slug):
    course_queue = Course.objects.filter(slug=course_slug)
    if course_queue.exists():
        course = course_queue.first()
    else:
        return

    # WILL BE CHANGED TO CURRENT USER
    s = request.user  # DO NOT KNOW IF THIS WORKS YET

    if not Enroll.objects.filter(user=s, cno=course):
        Enroll.objects.create(enroll_id=uuid.uuid1(), cno=course, user=s)
    else:
        Enroll.objects.filter(cno=course, user=s).delete()
    return redirect("courses:my_courses")
