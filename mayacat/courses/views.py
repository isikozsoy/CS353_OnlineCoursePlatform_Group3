from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import ListView, DetailView, View
from django.db import connections
from main.models import *
from courses.models import *
from accounts.models import *

from .forms import *

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

        cursor = connections['default'].cursor()

        course_queue = Course.objects.raw( '''SELECT * FROM courses_course WHERE slug = %s;''',[course_slug])

        #check whether the student is enrolled into this course
        #is course slug primary key

        curuser_id = request.user.id
        print(curuser_id)

        print("=1",course_queue)
        if len(course_queue) > 0:
            course = course_queue[0]
            print("=2",course, course.cno)
        else:
            #404 error
            print("error no course as the stated");

        lecture_q = Lecture.objects.raw( '''SELECT * FROM courses_lecture as CL WHERE CL.lecture_slug = %s;''',[lecture_slug])
        if len(lecture_q) > 0:
            lecture = lecture_q[0]
            print("=3","lecture exists\n")
        else:
            #error no such lecture
            print("error no lecture as the stated");
        print("=4",lecture_q)
        print("=5",lecture)
        isWatched = Progress.objects.raw('''SELECT * FROM main_progress as MP 
                                            WHERE MP.lecture_no_id = %s AND MP.s_username_id = %s;'''
                                            , [lecture.lecture_no, curuser_id])
        print(isWatched)

        cno = course.cno
        lectures = Lecture.objects.raw('''SELECT * FROM courses_lecture as CL WHERE CL.cno_id = %s;''', [cno])

        if (len(isWatched) == 0):
            cursor.execute('''INSERT INTO main_progress(lecture_no_id ,s_username_id) VALUES (%s, %s) ''',
                       [lecture.lecture_no, curuser_id])
            prog = Progress.objects.raw( '''SELECT MP.prog_id FROM main_progress as MP
                                            WHERE MP.s_username_id = %s AND 
                                                  MP.lecture_no_id IN ( SELECT lecture_no
                                                                        FROM courses_lecture 
                                                                        WHERE cno_id = %s );'''
                                              ,[curuser_id,cno])
            print("prog : ", len(prog))     #raw must include primary key - cursor
            if( len(prog) == len(lectures) ):
                print("This course is finished")
                return HttpResponseRedirect('/'+course_slug+'/'+lecture_slug+'/finish')


        lecandprog = [None] * len(lectures)
        for i in range(0,len(lectures)):
            isWatched = Progress.objects.raw( '''SELECT * FROM main_progress as MP 
                                                    WHERE MP.lecture_no_id = %s AND MP.s_username_id = %s;'''
                                              ,[lectures[i].lecture_no,curuser_id])
            print(isWatched)

            if(len(isWatched) > 0):
                lecandprog[i] = (lectures[i],"Watched")
            else:
                lecandprog[i] = (lectures[i], "Unwatched")


        announcements = Announcement.objects.raw('''SELECT * FROM main_announcement as MA WHERE MA.cno_id = %s;''', [cno])
        #announcements = Announcement.objects.filter(cno_id=course.cno)

        notes = Takes_note.objects.raw( '''SELECT * FROM main_takes_note as MTN 
                                            WHERE MTN.lecture_no_id = %s AND MTN.s_username_id = %s;''',
                                            [lecture.lecture_no, curuser_id])  # student will be added
        #notes = Takes_note.objects.filter(lecture_no_id=lecture.lecture_no)
        lecturecnt = len(lectures)

        questions = Post.objects.raw('''SELECT postno
                                        FROM main_post
                                        WHERE postno NOT IN (SELECT answer_no_id AS postno FROM main_quest_answ ) 
                                            AND lecture_no_id = %s; ''',[lecture.lecture_no])

        qanda = [None] * len(questions)

        answers = [None] * len(questions)
        for i in range(0,len(questions)):
            answers[i] = Quest_answ.objects.raw('''SELECT *
                                                 FROM main_quest_answ, main_post
                                                 WHERE question_no_id = %s AND answer_no_id = postno;''',[questions[i].postno])
            qanda[i] = (questions[i], answers[i])
        print(qanda)

        assignments =Assignment.objects.raw('''SELECT *
                                                 FROM main_assignment
                                                 WHERE lecture_no_id = %s;''',[lecture.lecture_no])
        assignmentcnt  = len(assignments)
        lecturemat = LectureMaterial.objects.raw('''SELECT *
                                                 FROM courses_lecturematerial
                                                 WHERE lecture_no_id = %s;''',[lecture.lecture_no])
        lecturematcnt = len(lecturemat)

        #contributors = Contributor.objects.raw( '''SELECT U.username
        #                                         FROM main_contributor AS MC,auth_user AS U
        #                                         WHERE MC.cno_id = %s AS MC.user_id = U.id;''',[course.cno] )

        context = {
            'curlecture': lecture,
            'course': course,
            'announcements': announcements,
            'notes': notes,
            'assignments' : assignments,
            'assignmentcnt' : assignmentcnt,
            'lecturemat' : lecturemat,
            'lecturematcnt' : lecturematcnt,
            'lecturecnt': lecturecnt,
            'qanda' : qanda,
            'lecandprog' : lecandprog,
            'url' : '/'+course_slug+'/'+lecture_slug
            #'contributors' : contributors
        }

        form = AskQuestion()
        print(form)
        return render(request, 'courses/lecture_detail.html', context)

    def post(self, request):
        form = AskQuestion(request.POST)
        if form.is_valid():
            question = form.cleaned_data['question']
            print("Question : ",question)




class CourseFinishView(View):
    def get(self, request, course_slug, lecture_slug, *args, **kwargs):
        context = {
            'curlecture': 'CURLECTURE'
        }
        return render(request, 'courses/course_finish.html', context)

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
