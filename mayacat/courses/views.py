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
        course_queue = Course.objects.raw( '''SELECT * FROM courses_course WHERE slug = %s;''',[course_slug])
        #course_queue = Course.objects.filter(slug=course_slug)

        #check whether the student is enrolled into this course
        #is course slug primary key

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

        cno = course.cno
        print("- ",cno)

        lectures = Lecture.objects.raw( '''SELECT * FROM courses_lecture as CL WHERE CL.cno_id = %s;''',[cno])
        #lectures = Lecture.objects.raw('''SELECT * FROM courses_lecture;''')
        print("=6",lecture_slug, course.cno, lectures, len(lectures))

        announcements = Announcement.objects.raw('''SELECT * FROM main_announcement as MA WHERE MA.cno_id = %s;''', [cno])
        #announcements = Announcement.objects.filter(cno_id=course.cno)

        notes = Takes_note.objects.raw( '''SELECT * FROM main_takes_note as MTN WHERE MTN.lecture_no_id = %s;''',
                                            [lecture.lecture_no])  # student will be added
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
            #qanda[i].append(questions[i])
            #if(len(answers[i]) > 0):
                #qanda[i].append(answers[i])
            tmpdict = {'question' : questions[i], 'answers' : answers[i]}
            print("tmpdict",tmpdict,len(answers[i]))
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

        context = {
            'curlecture': lecture,
            'course': course,
            'lectures': lectures,
            'announcements': announcements,
            'notes': notes,
            'assignments' : assignments,
            'assignmentcnt' : assignmentcnt,
            'lecturemat' : lecturemat,
            'lecturematcnt' : lecturematcnt,
            'lecturecnt': lecturecnt,
            'qanda' : qanda
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
