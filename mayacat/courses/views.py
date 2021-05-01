from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import ListView, DetailView
from django.views.generic.base import View
from django.db import connection
from main.models import *
from accounts.models import *
from .models import *
from .forms import *


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


# This class is not used in any place. I deleted it and nothing was affected.
class CourseListView(ListView):
    model = Course


class CourseDetailView(View):
    def get(self, request, slug, *args, **kwargs):
        form = GiftInfo()
        '''
        course_queue = Course.objects.raw('SELECT * FROM courses_course WHERE slug = %s', [slug])
        '''

        course = Course.objects.raw('SELECT * FROM courses_course WHERE slug = "' + slug + '" LIMIT 1')[0]
        cno = course.cno

        lecture_list = Lecture.objects.raw('SELECT * FROM courses_lecture WHERE cno_id = %s;', [cno])
        context = {
            'cname': course.cname,
            'desc': course.description,
            'slug': slug,
            'lecture_list': lecture_list,
            'form': form
        }
        return render(request, 'course_detail.html', context)

    def post(self, request, slug):
        print("icerdeyimm---------------------------------")
        form = GiftInfo(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            users = Student.objects.raw('SELECT * FROM accounts_student WHERE username = %s;',
                                        [username])
            if len(list(users)) == 0:
                pass
                # INVALID USER
            else:
                cursor = connection.cursor()
                receiver_id = users[0].user_id
                course_queue = Course.objects.raw('SELECT * FROM courses_course WHERE slug = %s', [slug])
                if len(list(course_queue)) != 0:
                    course = Course.objects.raw('SELECT * FROM courses_course WHERE slug = %s LIMIT 1', [slug])[0]
                    cno = course.cno
                else:
                    return

                cursor.execute('INSERT INTO main_gift (cno_id, user_id) VALUES (%s, %s);',
                               [cno, receiver_id])
                cursor.execute('INSERT INTO main_enroll (cno_id, user_id) VALUES (%s, %s);',
                               [cno, receiver_id])
                return HttpResponseRedirect('/')


class LectureView(View):
    # model = Lecture

    def get(self, request, slug, lecture_slug, *args, **kwargs):
        cursor = connection.cursor()
        course_queue = Course.objects.raw('SELECT * FROM courses_course WHERE slug = %s', [slug])
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
        # lectures_q = 'SELECT * FROM courses_lecture WHERE cno_id = %s'
        # lectures = cursor.execute(lectures_q, [cno])

        announcements = Announcement.objects.raw('SELECT * FROM main_announcement WHERE cno_id = %s', [cno])

        notes = Takes_note.objects.raw('SELECT * FROM main_takes_note WHERE lecture_no_id = %s', [lecture_no])

        lecturecnt = len(list(lectures))
        print(lecturecnt)

        row = cursor.execute('SELECT COUNT(lecture_no) FROM courses_lecture WHERE cno_id = %s', [cno])
        row = cursor.fetchone()
        lecturecnt = row[0]

        # print("lecturecnt: ", lecturecnt, ", len: ", len(list(lectures))) # both of them gives 0 for aaa but should give 2

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

        return render(request, 'lecture_detail.html', context)


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

    my_courses_q = ('SELECT * ' +
                    'FROM main_enroll ' +
                    'WHERE user_id = ' + str(user_id) + ' AND cno_id = ' + str(cno) + ';')
    my_courses = Enroll.objects.raw(my_courses_q)

    if len(list(my_courses)) == 0:
        insert_q = 'INSERT INTO main_enroll (cno_id, user_id) VALUES ' \
                   '(' + str(cno) + ', ' + str(user_id) + ');'
        cursor.execute(insert_q)
    else:
        # Once we buy the course we cannot delete it logical bence
        """
        cursor.execute('DELETE FROM main_enroll ' \
                       'WHERE user_id = ' + str(user_id) + ' AND cno_id = "' + str(cno) + '"')
    """
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
        Gift.objects.create(cno=course, user=s)
    else:
        Wishes.objects.filter(cno=course, user=s).delete()

    return redirect("courses:my_courses")
