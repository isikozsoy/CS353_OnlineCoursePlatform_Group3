from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import ListView, DetailView, View
from django.db import connection
from main.models import *
from .models import *


class MyCoursesView(ListView):
    def get(self, request):
        # WILL BE CHANGED TO CURRENT USER
        user_id = request.user.id
        my_courses_q = Enroll.objects.raw('''SELECT *
                                            FROM main_enroll
                                            WHERE user_id = %s''', [user_id])
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
        course_queue = Course.objects.raw('SELECT * FROM courses_course WHERE slug = %s', [course_slug])
        if len(list(course_queue)) != 0:
            course = course_queue[0]
            cno = course.cno
        else:
            return

        lecture_queue = Lecture.objects.raw('SELECT * FROM courses_lecture WHERE lecture_slug = %s', [lecture_slug])
        if len(list(lecture_queue)) != 0:
            lecture = lecture_queue[0]
            lecture_no = lecture.lecture_no
        else:
            return

        lectures = Lecture.objects.raw('SELECT * FROM courses_lecture WHERE cno_id = %s', [cno])

        announcements = Announcement.objects.raw('SELECT * FROM main_announcement WHERE cno_id = %s', [cno])

        notes = Takes_note.objects.raw('SELECT * FROM main_takes_note WHERE cno_id = %s', [cno])

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
    course_queue = Course.objects.raw('SELECT * FROM courses_course WHERE slug = %s', [course_slug])
    if len(list(course_queue)) != 0:
        course = Course.objects.raw('SELECT * FROM courses_course WHERE slug = %s LIMIT 1', [course_slug])[0]
        cno = course.cno
    else:
        return

    # WILL BE CHANGED TO CURRENT USER
    user_id = request.user.id
    cursor = connection.cursor()
    my_courses = Enroll.objects.raw('SELECT * FROM main_enroll WHERE user_id = %s',
                                    [user_id])

    if len(list(my_courses)) == 0:
        cursor.execute('INSERT INTO main_enroll (cno_id, user_id) VALUES (%s, %s);',
                       [cno, user_id])
    else:
        cursor.execute('DELETE FROM main_enroll WHERE cno_id = %s AND user_id = %s', [cno, user_id])
    return redirect("courses:my_courses")


def send_course_as_gift(request, course_slug, receiver):
    course_queue = Course.objects.raw('SELECT * FROM courses_course as C WHERE C.slug = %s', [course_slug])
    if len(list(course_queue)) != 0:
        course = Course.objects.raw('SELECT * FROM courses_course WHERE C.slug = %s LIMIT 1', [course_slug])[0]
        cno = course.cno
    else:
        return

        # WILL BE CHANGED TO CURRENT USER
        s = request.user

        if not Enroll.objects.raw('SELECT * FROM main_enroll as E WHERE E.cno_id = %s AND E.user_id= %', [cno]):
            Gift.objects.create(wishes_id=uuid.uuid1(), cno=course, user=s)
        else:
            Wishes.objects.filter(cno=course, user=s).delete()

    return redirect("courses:my_courses")