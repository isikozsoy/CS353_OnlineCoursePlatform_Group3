import sys

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import ListView
from django.views.generic.base import View
from django.db import connection, connections, DatabaseError, Error
from main.models import *
from courses.models import *
from accounts.models import *
from datetime import date
from slugify import slugify
from datetime import date
from PIL import Image, ImageDraw

from .forms import *
from main.views import get_user_type
from main.views import MainView
from accounts.views import LoginView


# from reportlab.pdfgen.canvas import Canvas


class MyCoursesView(ListView):
    def get(self, request):
        if request.user.is_authenticated:
            user_id = request.user.id
            cursor = connection.cursor()

            cursor.execute('''SELECT cc.cname, cc.slug, cc.cno, cc.course_img 
                            FROM main_enroll as me, courses_course as cc 
                            WHERE me.user_id = %s and me.cno_id = cc.cno''', [user_id])

            my_courses_q = cursor.fetchall()

            cursor.execute('select type '
                           'from user_types '
                           'where id = %s;', [user_id])

            row = cursor.fetchone()
            user_type = -1
            if row:
                user_type = row[0]

            my_courses = ()

            for course in my_courses_q:

                cursor.execute('''SELECT COUNT(lecture_no)
                                            FROM courses_lecture AS cl 
                                            WHERE cl.cno_id = %s AND 
                                            cl.cno_id IN (SELECT me.cno_id
                                                                FROM main_enroll AS me 
                                                                WHERE me.user_id = %s );''',
                               [course[2], request.user.id])

                total = cursor.fetchone()

                if total:
                    total = total[0]

                if (total is None or total == 0):
                    percentage = 100

                else:

                    cursor.execute('''SELECT COUNT(MP.lecture_no_id) FROM main_progress as MP
                                        WHERE MP.s_username_id = %s 
                                        AND MP.lecture_no_id IN 
                                            ( SELECT lecture_no
                                                FROM courses_lecture 
                                                WHERE cno_id = %s );''', [request.user.id, course[2]])
                    prog = cursor.fetchone()

                    if prog:
                        prog = prog[0]
                    else:
                        prog = 0

                    percentage = int(100 * prog / total)

                course = course + (percentage,)
                my_courses = my_courses + (course,)
            print(my_courses)

            topic_list = Topic.objects.raw('select topicname from main_topic;')
            context = {
                'my_courses_q': my_courses,
                'user_type': user_type,
                'topic_list': topic_list,
            }

            return render(request, 'main/my_courses.html', context)
        return HttpResponseRedirect('/')


def add_to_my_courses(request, course_slug):
    if not request.user.is_authenticated:  # if the user did not login, return to main page
        return HttpResponseRedirect('/')

    cursor = connection.cursor()
    course_queue = Course.objects.raw('SELECT * FROM courses_course WHERE slug = %s', [course_slug])
    if len(list(course_queue)) != 0:
        course = Course.objects.raw('SELECT * FROM courses_course WHERE slug = %s LIMIT 1', [course_slug])[0]
        cno = course.cno
    else:
        return HttpResponseRedirect('/')

    user_id = request.user.id

    my_courses = Enroll.objects.raw('SELECT * '
                                    'FROM main_enroll '
                                    'WHERE user_id = %s AND cno_id = %s;',
                                    [user_id, cno])

    if len(list(my_courses)) == 0:
        cursor.execute('INSERT INTO main_enroll (cno_id, user_id) VALUES (%s, %s);',
                       [cno, user_id])
    else:
        print("Inside else.........")
        # Once we buy the course we cannot delete it logical bence
        """
            cursor.execute('DELETE FROM main_enroll ' \
                           'WHERE user_id = ' + str(user_id) + ' AND cno_id = "' + str(cno) + '"')
        """
    cursor.close()
    return HttpResponseRedirect('/my_courses/add/')


class CourseListView(ListView):
    model = Course


class CourseDetailView(View):
    def get(self, request, course_slug, warning_message=None):
        form = GiftInfo()
        cursor = connection.cursor()

        course = Course.objects.raw('SELECT * FROM courses_course WHERE slug = %s;', [course_slug])
        if len(list(course)) != 0:
            course = course[0]
        else:
            return HttpResponseRedirect('/')
        cno = course.cno

        cursor.execute('SELECT * FROM courses_lecture WHERE cno_id = %s;', [cno])

        lecture_list = cursor.fetchall()

        if (len(lecture_list) > 0):
            lectures = [None] * len(lecture_list)
            for i in range(0, len(lecture_list)):
                lectures[i] = {
                    'lecture_slug': lecture_list[i][2],
                    'lecture_name': lecture_list[i][1],
                }
        else:
            lectures = None
        is_owner = False
        is_only_gift = False
        is_enrolled = 0
        if course.owner_id == request.user.id:
            is_owner = True
            is_only_gift = True

        else:
            cursor.execute('SELECT count(*) FROM main_enroll as E WHERE E.cno_id = %s AND E.user_id= %s',
                           [cno, request.user.id])
            is_enrolled = cursor.fetchone()

            if is_enrolled:
                is_enrolled = is_enrolled[0]

            is_in_cart = Inside_Cart.objects.raw(
                'SELECT * FROM main_inside_cart WHERE cno_id = %s AND username_id= %s AND '
                'receiver_username_id = %s', [cno, request.user.id, request.user.id])
            if is_enrolled or is_in_cart:
                is_only_gift = True

        is_wish = len(list(Wishes.objects.raw('SELECT * FROM main_wishes WHERE cno_id = %s AND user_id = %s;',
                                              [cno, request.user.id])))

        registered = len(list(Enroll.objects.raw('SELECT * FROM main_enroll WHERE cno_id = %s AND user_id = %s;',
                                                 [cno, request.user.id])))

        cursor.execute('''SELECT U.username 
                                FROM main_contributor AS MC,auth_user AS U
                                WHERE MC.cno_id = %s AND MC.user_id = U.id;''', [course.cno])

        contributor_list = cursor.fetchall()
        contributors = [None] * len(contributor_list)
        for i in range(0, len(contributors)):
            contributors[i] = contributor_list[i][0]
            print(contributor_list[i][0])

        lectures = Lecture.objects.raw('''SELECT * FROM courses_lecture as CL WHERE CL.cno_id = %s;''', [cno])
        lecture_count = len(lectures)

        cursor.execute('SELECT AVG(score) FROM main_finishes WHERE cno_id = %s AND score !=0', [cno])
        rating = cursor.fetchone()

        if rating:
            if rating[0]:
                rating = rating[0]
            else:
                rating = 0

        print("Rating:", rating)

        cursor.execute('SELECT * '
                       'FROM main_advertisement '
                       'WHERE cno_id = %s AND status = 2 '
                       'AND (CURRENT_TIMESTAMP BETWEEN startdate AND finishdate) ', [cno])

        advertisement_list = cursor.fetchone()
        print("advertisement", advertisement_list)

        advertisement = None

        if (advertisement_list is not None):
            advertisement = {
                'advertisement': advertisement_list[1]
            }

        cursor.execute('SELECT comment FROM main_finishes WHERE cno_id = %s;', [cno])

        comment_list = cursor.fetchall()
        comments = [None] * len(comment_list)
        is_All_None = True

        for i in range(0, len(comment_list)):
            if comment_list[i][0]:
                comments[i] = comment_list[i][0]
                is_All_None = False

        if is_All_None:
            comments = None

        cursor.execute('select type '
                       'from user_types '
                       'where id = %s;', [request.user.id])

        row = cursor.fetchone()
        user_type = -1
        if row:
            user_type = row[0]
        cursor.execute('SELECT count(*) '
                       'FROM main_wishes WHERE cno_id = %s AND user_id = %s;',
                       [cno, request.user.id])
        is_wish = cursor.fetchone()

        if is_wish:
            is_wish = is_wish[0]

        topic_list = Topic.objects.raw('select topicname from main_topic;')

        cursor.execute('''SELECT MAX(MP.lecture_no_id) 
                                    FROM main_progress as MP
                                    WHERE MP.s_username_id = %s 
                                    AND MP.lecture_no_id IN 
                                        ( SELECT lecture_no
                                        FROM courses_lecture 
                                        WHERE cno_id = %s );''', [request.user.id, cno])
        prog = cursor.fetchone()

        if prog:
            prog = prog[0]

        cursor.execute('''SELECT COUNT(MP.lecture_no_id)
                                            FROM main_progress as MP
                                            WHERE MP.s_username_id = %s 
                                            AND MP.lecture_no_id IN 
                                                ( SELECT lecture_no
                                                FROM courses_lecture 
                                                WHERE cno_id = %s );''', [request.user.id, cno])
        completed_lec_count = cursor.fetchone()

        if completed_lec_count:
            completed_lec_count = completed_lec_count[0]

        finished = False
        if completed_lec_count == len(lectures):
            finished = True

        lecture_slug = None

        if lecture_count != 0 and is_enrolled:
            if (prog is None or finished):
                cursor.execute('''SELECT MIN(lecture_no) FROM courses_lecture WHERE cno_id = %s''', [cno])
                min_lecture_no = cursor.fetchone()

                if min_lecture_no:
                    min_lecture_no = min_lecture_no[0]

                cursor.execute('''SELECT lecture_slug FROM courses_lecture 
                                            WHERE cno_id = %s AND lecture_no = %s ''', [cno, min_lecture_no])
                lecture_slug = cursor.fetchone()

                if lecture_slug:
                    lecture_slug = lecture_slug[0]

            else:
                cursor.execute('''SELECT lecture_slug FROM courses_lecture WHERE lecture_no > %s''', [prog])
                lecture_slug = cursor.fetchone()

                if lecture_slug:
                    lecture_slug = lecture_slug[0]

        cursor.execute('''SELECT count(*) FROM main_contributor AS MC
                          WHERE MC.cno_id = %s AND MC.user_id = %s;''', [course.cno, request.user.id])

        is_contributor = cursor.fetchone()[0]
        if is_contributor != 0:
            registered = True
            is_only_gift = True

        context = {
            'lecture_list': lectures,
            'form': form,
            'course': course,
            'is_wish': is_wish,
            'user_type': user_type,
            'path': request.path,
            'is_gift': is_only_gift,
            'topic_list': topic_list,
            'registered': registered,
            'lecture_count': lecture_count,
            'rating': rating,
            'advertisement': advertisement,
            'comments': comments,
            'is_owner': is_owner,
            'prog': prog,
            'lecture_slug': lecture_slug,
            'finished': finished,
            'contributors': contributors,
            'contributor_cnt': len(contributors),
            'warning_message': warning_message,
        }

        cursor.close()
        return render(request, 'courses/course_detail.html', context)

    def post(self, request, course_slug):
        form = GiftInfo(request.POST)
        course = Course.objects.raw('SELECT * FROM courses_course WHERE slug = %s;', [course_slug])[0]
        cno = course.cno

        cursor = connection.cursor()
        if form.is_valid():
            if not form.cleaned_data['is_gift']:
                cursor.execute('INSERT INTO main_inside_cart (cno_id, receiver_username_id, username_id)'
                               'VALUES (%s, %s, %s);',
                               [cno, request.user.id, request.user.id])  # own id if it is not a gift
                cursor.close()
                return redirect("main:cart")

        cursor.execute('INSERT INTO main_inside_cart (cno_id, receiver_username_id, username_id)'
                       'VALUES (%s, %s, %s);', [cno, None, request.user.id])  # -1 if it is a gift

        return redirect("main:cart")


class AddAsGift(View):
    def post(self, request, course_slug):
        # form = AddAsGift(request.POST)
        course = Course.objects.raw('SELECT * FROM courses_course WHERE slug = %s;', [course_slug])[0]
        cno = course.cno

        cursor = connection.cursor()

        cursor.execute('INSERT INTO main_inside_cart (cno_id, receiver_username_id, username_id)'
                       'VALUES (%s, %s, %s);', [cno, None, request.user.id])  # -1 if it is a gift

        return redirect("main:cart")


def add_gift_to_cart(request, course_slug):
    course = Course.objects.raw('SELECT * FROM courses_course WHERE slug = %s;', [course_slug])[0]
    cno = course.cno

    cursor = connection.cursor()
    print("---------------3.gift---------------")
    cursor.execute('INSERT INTO main_inside_cart (cno_id, receiver_username_id, username_id)'
                   'VALUES (%s, %s, %s);', [cno, None, request.user.id])  # -1 if it is a gift
    return redirect("main:cart")


class AddAnswerView(View):
    # model = Lecture

    def get(self, request, course_slug, lecture_slug, question_no, *args, **kwargs):
        answer = "to be completed"
        form = AnswerQuestion()

        topic_list = Topic.objects.raw('select * from main_topic;')

        context = {
            'question_no': question_no,
            'answer': answer,
            'topic_list': topic_list
        }
        return render(request, 'courses/add_answer.html', context)

    def post(self, request, course_slug, lecture_slug, question_no, *args, **kwargs):
        form = AnswerQuestion(request.POST)
        cursor = connection.cursor()
        if form.is_valid():
            answer = form.cleaned_data['answer']
        print("course_slug", course_slug, "lecture_slug", lecture_slug, "question_no ", question_no)
        cursor.execute('select lecture_no from courses_lecture where lecture_slug = %s;', [lecture_slug])
        lecture_no_row = cursor.fetchone()
        cursor.close()
        if not lecture_no_row:
            warning_message = "Error: There is no lecture with this name."
            return MainView.get(self, request, warning_message)

        cursor = connection.cursor()

        lecture_no = lecture_no_row[0]
        cursor.execute(
            'insert into main_post (post, lecture_no_id, username_id, date) values (%s, %s, %s,CURRENT_TIMESTAMP );',
            [answer, lecture_no, request.user.id])
        cursor.execute('select LAST_INSERT_ID()')
        row = cursor.fetchone()
        print("row", row)
        if row:
            ans_no = row[0]
            print("In post of addanswerview", ans_no)
            cursor.execute('insert into main_quest_answ (answer_no_id, question_no_id) values (%s, %s);',
                           [ans_no, question_no])
        cursor.close()
        return HttpResponseRedirect("/" + course_slug + "/" + lecture_slug)


class LectureView(View):
    # model = Lecture

    def get(self, request, course_slug, lecture_slug, warning_message=None, *args, **kwargs):
        cursor = connection.cursor()
        if not request.user.id:
            return HttpResponseRedirect("/login")

        course_queue = Course.objects.raw('''SELECT * FROM courses_course WHERE slug = %s;''', [course_slug])
        print(request.user.id)

        print("=1", course_queue)
        if len(course_queue) > 0:
            course = course_queue[0]
            print("=2", course, course.cno)
        else:
            return HttpResponseRedirect("/")

        cursor.execute('''SELECT U.username 
                                    FROM main_contributor AS MC,auth_user AS U
                                    WHERE MC.cno_id = %s AND MC.user_id = U.id AND U.id = %s;''',
                       [course.cno, request.user.id])
        isContributor = (course.owner_id == request.user.id)
        if cursor.fetchone():
            isContributor = True

        cursor.execute('''SELECT enroll_id FROM main_enroll WHERE cno_id = %s AND user_id = %s''',
                       [course.cno, request.user.id])
        if not isContributor and not cursor.fetchone():
            return HttpResponseRedirect("/" + course_slug)

        cursor.execute('''SELECT username FROM auth_user WHERE id = %s;''', [course.owner_id])
        owner_username = cursor.fetchone()[0]

        lecture_q = Lecture.objects.raw('''SELECT * FROM courses_lecture as CL WHERE CL.lecture_slug = %s;''',
                                        [lecture_slug])
        if len(lecture_q) > 0:
            lecture = lecture_q[0]
            print("=3", "lecture exists\n")
        else:
            # error no such lecture
            print("error no lecture as the stated");

        curuser_id = request.user.id
        print("=4", lecture_q)
        print("=5", lecture)
        isWatched = Progress.objects.raw('''SELECT * FROM main_progress as MP 
                                            WHERE MP.lecture_no_id = %s AND MP.s_username_id = %s;'''
                                         , [lecture.lecture_no, curuser_id])
        print(isWatched)

        cno = course.cno
        lectures = Lecture.objects.raw('''SELECT * FROM courses_lecture as CL WHERE CL.cno_id = %s;''', [cno])
        isFinished = 0
        if (len(isWatched) == 0):
            cursor.execute('''INSERT INTO main_progress(lecture_no_id ,s_username_id) VALUES (%s, %s); ''',
                           [lecture.lecture_no, curuser_id])
            prog = Progress.objects.raw('''SELECT MP.prog_id FROM main_progress as MP
                                            WHERE MP.s_username_id = %s AND 
                                                  MP.lecture_no_id IN ( SELECT lecture_no
                                                                        FROM courses_lecture 
                                                                        WHERE cno_id = %s );'''
                                        , [curuser_id, cno])
            print("prog : ", len(prog))  # raw must include primary key - cursor

        prog = Progress.objects.raw('''SELECT MP.prog_id FROM main_progress as MP
                                                    WHERE MP.s_username_id = %s AND 
                                                          MP.lecture_no_id IN ( SELECT lecture_no
                                                                                FROM courses_lecture 
                                                                                WHERE cno_id = %s );'''
                                    , [curuser_id, cno])
        if (len(prog) == len(lectures) and not isContributor and course.is_complete == 1):
            cursor.execute('''SELECT user_id FROM main_finishes WHERE cno_id = %s and user_id = %s;''',
                           [cno, curuser_id])
            if not cursor.fetchone():
                cursor.execute('''INSERT INTO main_finishes(comment,cno_id,user_id,score) VALUES (%s,%s, %s,%s);''',
                               ["", cno, curuser_id, 0])
            print("This course is finished")
            isFinished = 1

        print("- ", cno)

        # lectures = Lecture.objects.raw('''SELECT * FROM courses_lecture;''')
        print("=6", lecture_slug, course.cno, lectures, len(lectures))

        lecandprog = [None] * len(lectures)
        for i in range(0, len(lectures)):
            isWatched = Progress.objects.raw('''SELECT * FROM main_progress as MP 
                                                    WHERE MP.lecture_no_id = %s AND MP.s_username_id = %s;'''
                                             , [lectures[i].lecture_no, curuser_id])
            print(isWatched)

            if (len(isWatched) > 0):
                lecandprog[i] = (lectures[i], "Watched")
            else:
                lecandprog[i] = (lectures[i], "Unwatched")

        cursor.execute('''SELECT COUNT(MP.prog_id) FROM main_progress as MP
                                                    WHERE MP.s_username_id = %s AND 
                                                          MP.lecture_no_id IN ( SELECT lecture_no
                                                                                FROM courses_lecture 
                                                                                WHERE cno_id = %s );'''
                       , [curuser_id, cno])
        cnt_prog = cursor.fetchone()[0]

        cursor.execute('''SELECT COUNT(lecture_no) FROM courses_lecture as CL WHERE CL.cno_id = %s;''', [cno])
        cnt_lec = cursor.fetchone()[0]

        print("Progress and lecture count : ", cnt_prog, cnt_lec)

        avg_prog = (cnt_prog / cnt_lec) * 100

        announcements = Announcement.objects.raw('''SELECT * FROM main_announcement as MA,auth_user as U 
                                                    WHERE MA.cno_id = %s and MA.i_user_id = U.id;''', [cno])
        # announcements = Announcement.objects.filter(cno_id=course.cno)

        notes = Takes_note.objects.raw('''SELECT * FROM main_takes_note as MTN 
                                            WHERE MTN.lecture_no_id = %s AND MTN.s_username_id = %s;''',
                                       [lecture.lecture_no, curuser_id])
        newNote = NewNoteForm()
        lecturecnt = len(lectures)

        questions = Post.objects.raw('''SELECT postno
                                        FROM main_post
                                        WHERE postno NOT IN (SELECT answer_no_id AS postno FROM main_quest_answ ) 
                                            AND lecture_no_id = %s; ''', [lecture.lecture_no])

        qanda = [None] * len(questions)

        answers = [None] * len(questions)
        for i in range(0, len(questions)):
            answers[i] = Quest_answ.objects.raw('''SELECT *
                                                 FROM main_quest_answ, main_post
                                                 WHERE question_no_id = %s AND answer_no_id = postno;''',
                                                [questions[i].postno])
            qanda[i] = (questions[i], answers[i])
        print(qanda)

        assignments = Assignment.objects.raw('''SELECT *
                                                 FROM main_assignment
                                                 WHERE lecture_no_id = %s;''', [lecture.lecture_no])
        assignmentcnt = len(assignments)
        lecturemat = LectureMaterial.objects.raw('''SELECT *
                                                 FROM courses_lecturematerial
                                                 WHERE lecture_no_id = %s;''', [lecture.lecture_no])
        lecturematcnt = len(lecturemat)

        cursor.execute('''SELECT U.username 
                        FROM main_contributor AS MC,auth_user AS U
                        WHERE MC.cno_id = %s AND MC.user_id = U.id;''', [course.cno])

        contributor_list = cursor.fetchall()
        contributors = [None] * len(contributor_list)
        for i in range(0, len(contributors)):
            contributors[i] = contributor_list[i][0]
            print(contributor_list[i][0])
        print("Contributors:", contributors)

        cursor.execute('''SELECT U.username 
                                FROM main_teaches AS MT,auth_user AS U
                                WHERE MT.lecture_no_id = %s AND MT.user_id = U.id;''', [lecture.lecture_no])

        teaches_list = cursor.fetchall()
        teaches = [None] * len(teaches_list)
        for i in range(0, len(teaches)):
            teaches[i] = teaches_list[i][0]
            print(teaches_list[i][0])
        print("Teaches:", teaches)

        form_lecmat_assignment = CreateAssignmentAndLectureMaterialForm()

        cursor = connection.cursor()
        cursor.execute('select type '
                       'from user_types '
                       'where id = %s;', [request.user.id])

        row = cursor.fetchone()
        user_type = -1
        if row:
            user_type = row[0]

        form_teacher = AddTeacherForm()

        form_question = AskQuestion()

        add_announcement = AddAnnouncementForm()
        topic_list = Topic.objects.raw('select topicname from main_topic;')
        context = {
            'curlecture': lecture,
            'course': course,
            'announcements': announcements,
            'notes': notes,
            'assignments': assignments,
            'assignmentcnt': assignmentcnt,
            'lecturemat': lecturemat,
            'lecturematcnt': lecturematcnt,
            'lecturecnt': lecturecnt,
            'qanda': qanda,
            'lecandprog': lecandprog,
            'url': '/' + course_slug + '/' + lecture_slug,
            'contributors': contributors,
            'form_lecmat_assignment': form_lecmat_assignment,
            'user_type': user_type,
            'topic_list': topic_list,
            'isFinished': isFinished,
            'teaches': teaches,
            'avg_prog': avg_prog,
            'isContributor': isContributor and (course.is_complete == 0),
            'owner_username': owner_username,
            'warning_message': warning_message
        }
        cursor.close()

        return render(request, 'courses/lecture_detail.html', context)

    def post(self, request, course_slug, lecture_slug, *args, **kwargs):
        cursor = connection.cursor()

        form_lecmat = CreateAssignmentAndLectureMaterialForm(request.POST)

        cursor.execute('select lecture_no from courses_lecture where lecture_slug = %s;', [lecture_slug])
        lecture_no_row = cursor.fetchone()
        cursor.close()
        if not lecture_no_row:
            warning_message = "Error: There is no lecture with this name."
            return MainView.get(self, request, warning_message)

        lecture_no = lecture_no_row[0]
        cursor = connection.cursor()

        if form_lecmat.is_valid():
            pdf_url_assignment = form_lecmat.cleaned_data['pdf_url_assignment']
            pdf_url_lecmat = form_lecmat.cleaned_data['pdf_url_lecmat']
            print("Assignment URL: ", pdf_url_assignment)
            print("Lecmat URL: ", pdf_url_lecmat)

            if pdf_url_lecmat:
                cursor.execute('insert into courses_lecturematerial (material, lecture_no_id) values (%s, %s);',
                               [pdf_url_lecmat, lecture_no])
            if pdf_url_assignment:
                cursor.execute('insert into main_assignment (assignment, lecture_no_id) values (%s, %s);',
                               [pdf_url_assignment, lecture_no])

        form_teacher = AddTeacherForm(request.POST)
        if form_teacher.is_valid():
            t_username = form_teacher.cleaned_data['addteacher']
            print("t_username", t_username)
            cursor.execute('SELECT id from auth_user where username = %s', [t_username])
            t_id_list = cursor.fetchone()
            if not t_id_list:
                response_str = 'There is no teacher with this username. <a href="/'
                response_str += request.path
                response_str += '">Return to lecture page...</a>'
                return HttpResponse(response_str)

            t_id = t_id_list[0]

            cursor.execute('''SELECT user_id from main_teaches WHERE lecture_no_id = %s and user_id = %s''',
                           [lecture_no, t_id])
            if not cursor.fetchone():
                cursor.execute('INSERT INTO main_teaches(lecture_no_id,user_id) VALUES (%s,%s);', [lecture_no, t_id])

        form_note = NewNoteForm(request.POST)
        if form_note.is_valid():
            newnote = form_note.cleaned_data['note']
            cursor.execute('INSERT INTO main_takes_note(note,lecture_no_id, s_username_id ) VALUES(%s,%s,%s);',
                           [newnote, lecture_no, request.user.id])

        form_question = AskQuestion(request.POST)
        if form_question.is_valid():
            question = form_question.cleaned_data['question']
            print("Question : ", question)
            cursor.execute(
                'insert into main_post (post, date, lecture_no_id, username_id) values (%s, curdate(), %s, %s);',
                [question, lecture_no, request.user.id])

        course_queue = Course.objects.raw('''SELECT * FROM courses_course WHERE slug = %s;''', [course_slug])
        if len(course_queue) > 0:
            course = course_queue[0]

        add_announcement = AddAnnouncementForm(request.POST)
        if add_announcement.is_valid():
            newannouncement = add_announcement.cleaned_data['addannouncement']
            cursor.execute('''insert into main_announcement (ann_date, ann_text, cno_id,i_user_id)
                                values (curdate(),%s, %s, %s);''',
                           [newannouncement, course.cno, request.user.id])

        cursor.close()
        return HttpResponseRedirect(request.path)


class DeleteTeacherView(View):
    def post(self, request, course_slug, lecture_slug, t_username, *args, **kwarg):

        cursor = connection.cursor()

        cursor.execute('SELECT id FROM auth_user WHERE username = %s;', [t_username])
        t_id_list = cursor.fetchone()
        if (t_id_list == None):
            warning_message = "Error: There is no teacher with this username"
            return LectureView.get(self, request, course_slug, lecture_slug, warning_message)

        t_id = t_id_list[0];
        print(t_id)
        cursor.execute('select lecture_no from courses_lecture where lecture_slug = %s;', [lecture_slug])
        lecture_no_row = cursor.fetchone()
        if not lecture_no_row:
            warning_message = "Error: There is no lecture with this name."
            return MainView.get(self, request, warning_message)

        lecture_no = lecture_no_row[0]

        cursor.execute('DELETE FROM main_teaches WHERE user_id = %s and lecture_no_id = %s;', [t_id, lecture_no])
        cursor.close()
        warning_message = "Success: Teacher successfully deleted"
        return LectureView.get(self, request, course_slug, lecture_slug, warning_message)


class DeleteAssignmentView(View):
    def post(self, request, course_slug, lecture_slug, a_id, *args, **kwarg):
        cursor = connection.cursor()

        cursor.execute('select lecture_no from courses_lecture where lecture_slug = %s;', [lecture_slug])
        lecture_no_row = cursor.fetchone()
        if not lecture_no_row:
            cursor.close()
            return HttpResponseRedirect("/" + course_slug + "/" + lecture_slug)

        lecture_no = lecture_no_row[0]

        cursor.execute('DELETE FROM main_assignment WHERE assignmentno = %s AND lecture_no_id = %s',
                       [a_id, lecture_no])

        cursor.close()
        return HttpResponseRedirect("/" + course_slug + "/" + lecture_slug)


class DeleteLectureMaterialView(View):
    def post(self, request, course_slug, lecture_slug, lm_id, *args, **kwarg):
        cursor = connection.cursor()

        cursor.execute('select lecture_no from courses_lecture where lecture_slug = %s;', [lecture_slug])
        lecture_no_row = cursor.fetchone()
        if not lecture_no_row:
            cursor.close()
            return HttpResponseRedirect("/" + course_slug + "/" + lecture_slug)

        lecture_no = lecture_no_row[0]

        cursor.execute('DELETE FROM courses_lecturematerial WHERE materialno = %s AND lecture_no_id = %s',
                       [lm_id, lecture_no])

        cursor.close()
        return HttpResponseRedirect("/" + course_slug + "/" + lecture_slug)


class DeleteAnnouncementView(View):
    def post(self, request, course_slug, lecture_slug, ann_id, *args, **kwarg):
        cursor = connection.cursor()

        cursor.execute('select cno from courses_course where slug = %s;', [course_slug])
        cno_row = cursor.fetchone()
        if not cno_row:  # no course with this course slug (i.e. URL)
            return HttpResponseRedirect("/" + course_slug + "/" + lecture_slug)  # return to main page
        cno = cno_row[0]

        cursor.execute('DELETE FROM main_announcement WHERE ann_id = %s AND cno_id = %s', [ann_id, cno])

        cursor.close()
        return HttpResponseRedirect("/" + course_slug + "/" + lecture_slug)


class DeleteNoteView(View):
    def post(self, request, course_slug, lecture_slug, note_id, *args, **kwarg):
        cursor = connection.cursor()

        cursor.execute('DELETE FROM main_takes_note WHERE note_id = %s;', [note_id])
        cursor.close()
        return HttpResponseRedirect("/" + course_slug + "/" + lecture_slug)


class DeleteQuestionView(View):
    def post(self, request, course_slug, lecture_slug, q_id, *args, **kwarg):
        cursor = connection.cursor()

        cursor.execute('DELETE FROM main_quest_answ WHERE question_no_id = %s;''', [q_id])

        cursor.execute('DELETE FROM main_post WHERE postno = %s;', [q_id])
        cursor.close()
        return HttpResponseRedirect("/" + course_slug + "/" + lecture_slug)


class DeleteAnswerView(View):
    def post(self, request, course_slug, lecture_slug, a_id, *args, **kwarg):
        cursor = connection.cursor()

        cursor.execute('DELETE FROM main_quest_answ WHERE answer_no_id = %s;''', [a_id])

        cursor.execute('DELETE FROM main_post WHERE postno = %s;', [a_id])
        cursor.close()
        return HttpResponseRedirect("/" + course_slug + "/" + lecture_slug)


class CourseCertificateView(View):
    def get(self, request, course_slug, *args, **kwargs):
        if not request.user.id:
            return HttpResponseRedirect("/login")

        cursor = connections['default'].cursor()

        course_queue = Course.objects.raw('''SELECT * FROM courses_course WHERE slug = %s;''', [course_slug])

        curuser_id = request.user.id
        print(curuser_id)

        cursor.execute('''SELECT username,first_name, last_name FROM auth_user WHERE id = %s''', [curuser_id])
        user = cursor.fetchone()
        username = user[0]
        first_name = user[1]
        last_name = user[2]
        print("certificate username:", username, first_name, last_name)
        """
                img = Image.new('RGB', (100, 30), color=(73, 109, 137))
        
                d = ImageDraw.Draw(img)
                d.text((10, 10), "Hello World", fill=(255, 255, 0))
        
                canvas = Canvas("certificate.pdf")
                canvas.drawString(72, 72, "Congratulations")
                canvas.save()
        """
        if len(course_queue) > 0:
            course = course_queue[0]
        else:
            # 404 error
            return HttpResponseRedirect('/')

        finish_list = Finishes.objects.raw(
            '''SELECT * FROM main_finishes as MF WHERE MF.cno_id = %s AND MF.user_id = %s;''',
            [course.cno, curuser_id])

        if (not finish_list):
            return HttpResponseRedirect("/" + course_slug)

        cursor.execute('select type '
                       'from user_types '
                       'where id = %s;', [request.user.id])

        row = cursor.fetchone()
        user_type = -1
        if row:
            user_type = row[0]

        topic_list = Topic.objects.raw('select * from main_topic;')

        context = {
            'courseurl': '/' + course_slug,
            'curcourse': course,
            'user': curuser_id,
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'user_type': user_type,
            'topic_list': topic_list,
            'course_slug': course_slug,
            #'pdf': canvas
        }
        cursor.close()

        return render(request, 'courses/coursecertificate.html', context)


class CourseFinishView(View):
    def get(self, request, course_slug, *args, **kwargs):

        if not request.user.id:
            return HttpResponseRedirect("/login")

        cursor = connections['default'].cursor()

        course_queue = Course.objects.raw('''SELECT * FROM courses_course WHERE slug = %s;''', [course_slug])

        curuser_id = request.user.id
        print(curuser_id)

        cursor.execute('''SELECT username FROM auth_user WHERE id = %s''', [curuser_id])
        username = cursor.fetchone()[0];

        if len(course_queue) > 0:
            course = course_queue[0]
        else:
            # 404 error
            print("error no course as the stated");

        finish_list = Finishes.objects.raw(
            '''SELECT * FROM main_finishes as MF WHERE MF.cno_id = %s AND MF.user_id = %s;''',
            [course.cno, curuser_id])

        if (not finish_list):
            return HttpResponseRedirect("/" + course_slug)
        finish_list = Finishes.objects.raw(
            '''SELECT * FROM main_finishes as MF WHERE MF.cno_id = %s AND MF.user_id = %s;''',
            [course.cno, curuser_id])
        currate = finish_list[0].score
        curcomment = finish_list[0].comment

        comment = FinishCourseCommentForm()
        rate = FinishCourseRateForm()
        first_last_name = FirstLastName()

        cursor.execute('select type '
                       'from user_types '
                       'where id = %s;', [request.user.id])

        row = cursor.fetchone()
        user_type = -1
        if row:
            user_type = row[0]

        topic_list = Topic.objects.raw('select * from main_topic;')

        context = {
            'currate': currate,
            'curcomment': curcomment,
            'url': '/' + course_slug + '/finish',
            'curcourse': course,
            'user': curuser_id,
            'username': username,
            'user_type': user_type,
            'topic_list': topic_list,
            'form': rate,
            'course_slug': course_slug,
            'first_last_name': first_last_name,
        }
        cursor.close()
        return render(request, 'courses/coursefinish.html', context)

    def post(self, request, course_slug, *args, **kwargs):
        cursor = connection.cursor()

        # cursor.execute('select lecture_no from courses_lecture where lecture_slug = %s;', [lecture_slug])
        course_queue = Course.objects.raw('''SELECT * FROM courses_course WHERE slug = %s;''', [course_slug])

        curuser_id = request.user.id
        print(curuser_id)

        if len(course_queue) > 0:
            course = course_queue[0]
        else:
            # 404 error
            print("error no course as the stated");
        form_comment = FinishCourseCommentForm(request.POST)

        if form_comment.is_valid():
            comment = form_comment.cleaned_data['comment']
            print("Comment: ", comment)
            cursor.execute('UPDATE main_finishes SET comment = %s where cno_id = %s AND user_id = %s;',
                           [comment, course.cno, curuser_id])

        form_rate = FinishCourseRateForm(request.POST)
        print("form_rate: ", form_rate)

        if form_rate.is_valid():
            rate_s = form_rate.cleaned_data.get("rate")
            print("Rate: ", rate_s)
            if rate_s == 'one':
                rate = 1
            elif rate_s == 'two':
                rate = 2
            elif rate_s == 'three':
                rate = 3
            elif rate_s == 'four':
                rate = 4
            elif rate_s == 'five':
                rate = 5
            cursor.execute('UPDATE main_finishes SET score = %s where cno_id = %s AND user_id = %s;',
                           [int(rate), course.cno, curuser_id])
        cursor.close()

        first_last_name = FirstLastName(request.POST)
        if first_last_name.is_valid():
            first_name = first_last_name.cleaned_data['first_name']
            last_name = first_last_name.cleaned_data['last_name']

            cursor.execute('update auth_user set first_name = %s, last_name = %s where id = %s;',
                           [first_name, last_name, request.user.id])
        return HttpResponseRedirect(request.path)


class AddComplainView(View):
    template_name = "main/complain.html"
    course_slug = ""

    def get(self, request, course_slug):
        form = ComplainForm()
        self.course_slug = course_slug
        if request.user.is_authenticated:  # we need to check enrollments as well
            cursor = connection.cursor()
            cursor.execute('select type '
                           'from user_types '
                           'where id = %s;', [request.user.id])

            row = cursor.fetchone()
            user_type = -1
            if row:
                user_type = row[0]

            topic_list = Topic.objects.raw('select * from main_topic;')

            return render(request, self.template_name, {'form': form,
                                                        'user_type': user_type,
                                                        'topic_list': topic_list, })
        warning_message = "You need to log in"
        return LoginView.get(self, request, warning_message)

    def post(self, request, course_slug):
        cursor = connection.cursor()
        self.course_slug = course_slug
        course_q = Course.objects.raw('select * '
                                      'from courses_course '
                                      'where slug = %s;',
                                      [self.course_slug])
        course = course_q[0]
        course_cno = course.cno

        form = ComplainForm(request.POST)
        if form.is_valid():
            description = form.cleaned_data['description']
            cursor.execute('insert into main_complaint (creation_date, description, course_id, s_user_id) '
                           'values (%s, %s, %s, %s);',
                           [get_today(), description, course_cno, request.user.id])
            cursor.close()
            return render(request, "trivial/success_message_after_submitting.html",
                          {'success_message': 'Your refund request has been sent to the administrators. '
                                              'You will get an answer in approximately a week. Please be patient.',
                           'course_slug': course_slug})
        cursor.close()
        return HttpResponseRedirect('/')


class RefundRequestView(View):
    template_name = "main/refund.html"
    course_slug = ""

    def get(self, request, course_slug):
        form = ComplainForm()
        self.course_slug = course_slug
        if request.user.is_authenticated:  # we need to check enrollments as well
            cursor = connection.cursor()
            cursor.execute('select type '
                           'from user_types '
                           'where id = %s;', [request.user.id])

            row = cursor.fetchone()
            user_type = -1
            if row:
                user_type = row[0]

            topic_list = Topic.objects.raw('select * from main_topic;')

            return render(request, self.template_name, {'form': form,
                                                        'user_type': user_type,
                                                        'topic_list': topic_list, })
        return HttpResponseRedirect('/')

    def post(self, request, course_slug):
        cursor = connection.cursor()
        self.course_slug = course_slug
        course_q = Course.objects.raw('select * '
                                      'from courses_course '
                                      'where slug = %s;',
                                      [self.course_slug])
        course = course_q[0]
        course_cno = course.cno

        form = ComplainForm(request.POST)
        if form.is_valid():
            description = form.cleaned_data['description']
            cursor.execute('INSERT INTO main_refundrequest (reason, status, cno_id, s_username_id) '
                           'VALUES (%s, %s, %s, %s);',
                           [description, 0, course_cno, request.user.id])
            cursor.close()
            return render(request, "trivial/success_message_after_submitting.html",
                          {'success_message': 'Your refund request has been sent to the administrators. '
                                              'You will get an answer in approximately a week. Please be patient.',
                           'course_slug': course_slug})
        cursor.close()
        return HttpResponseRedirect('/')


def make_slug_for_url(name, for_course=True):
    orig_slug = slugify(name)

    # check for the existence of the same slug below so that the slug is unique
    unique = False
    uniquifier = 1
    slug = orig_slug
    while not unique:
        cursor = connection.cursor()
        if for_course:
            cursor.execute('select count(*) from courses_course where slug = %s;', [orig_slug])
        else:
            cursor.execute('select count(*) from courses_lecture where lecture_slug = %s;', [orig_slug])
        count = cursor.fetchone()

        if count:
            count = count[0]

        cursor.close()
        if count != 0:
            orig_slug = slug + '-' + str(uniquifier)
            print("Result slug: ", orig_slug)
            uniquifier += 1
        else:
            unique = True

    return orig_slug


class AddCourseView(View):
    template_name = "courses/add_course.html"

    def get(self, request):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/')
        cursor = connection.cursor()

        cursor.execute('select count(*) '
                       'from accounts_instructor '
                       'where student_ptr_id = %s;', [request.user.id])
        is_instructor = cursor.fetchone()

        if is_instructor:
            is_instructor = is_instructor[0]

        cursor.close()

        if is_instructor == 0:  # this means that there is no instructor with the requested id
            return HttpResponseRedirect('/')  # TODO: A page to transform student into instructor

        form = CreateCourseForm()

        cursor = connection.cursor()
        cursor.execute('select type '
                       'from user_types '
                       'where id = %s;', [request.user.id])

        row = cursor.fetchone()
        user_type = -1
        if row:
            user_type = row[0]

        topic_list = Topic.objects.raw('select * from main_topic order by topicname;')

        return render(request, self.template_name, {'user_type': user_type,
                                                    'form': form,
                                                    'add_message': 'Add a course as an instructor:',
                                                    'create_button': 'Create a course!',
                                                    'topic_list': topic_list})

    def post(self, request):
        form = CreateCourseForm(request.POST, request.FILES)

        if form.is_valid():
            cname = form.cleaned_data['cname']
            price = form.cleaned_data['price']
            topics = form.cleaned_data.get('topic')
            thumbnail = form.cleaned_data['course_img']

            description = form.cleaned_data['description']
            private = form.cleaned_data['private']

            orig_slug = make_slug_for_url(cname)

            cursor = connection.cursor()
            try:
                cursor.execute('insert into courses_course (cname, price, slug, is_private, course_img, '
                               'description, owner_id) VALUES (%s, %s, %s, %s, %s, %s, %s);',
                               [cname, price, orig_slug, private, thumbnail, description, request.user.id])
            finally:
                cursor.close()

            cursor = connection.cursor()
            try:
                cursor.execute('select cno from courses_course where cname = %s;', [cname])
                cno = cursor.fetchone()

                if cno:
                    cno = cno[0]

                for topic in topics:
                    cursor.execute('insert into main_course_topic (cno_id, topicname_id) VALUES (%s, %s);',
                                   [cno, topic])
            except Error:
                return HttpResponse("There was an error.<p> " + str(sys.exc_info()))
            finally:
                cursor.close()

        warning_message = "Success: Course submission is successful."
        return MainView.get(self, request, warning_message)


class AddLectureToCourseView(View):
    template_name = "courses/add_course.html"

    def get(self, request, course_slug):
        cursor = connection.cursor()
        cursor.execute('select owner_id, cname, cno from courses_course where slug = %s;', [course_slug])
        cno_row = cursor.fetchone()
        cursor.close()
        if not cno_row:  # no course with this course slug (i.e. URL)
            warning_message = "No course with this name"
            return MainView.get(self, request, warning_message)

        owner_id = cno_row[0]
        cname = cno_row[1]
        cno = cno_row[2]
        # if the owner is not the user logging in, return to main page
        if request.user.id != owner_id:
            warning_message = "You cannot access this page"
            return MainView.get(self, request, warning_message)

        cursor = connection.cursor()
        cursor.execute('select is_complete from courses_course where cno = %s;', [cno])
        is_complete = cursor.fetchone()[0]
        if is_complete == 1:
            warning_message = "Error: You cannot add any more lectures to this course. The course is marked as complete."
            return CourseDetailView.get(self, request, warning_message)

        message = 'Add a lecture to ' + cname

        form = CreateLectureForm()

        cursor = connection.cursor()
        cursor.execute('select type '
                       'from user_types '
                       'where id = %s;', [request.user.id])

        row = cursor.fetchone()
        user_type = -1
        if row:
            user_type = row[0]

        topic_list = Topic.objects.raw('select * from main_topic order by topicname;')

        return render(request, self.template_name, {'user_type': user_type, 'form': form, 'add_message': message,
                                                    'create_button': 'Create a lecture!',
                                                    'topic_list': topic_list, })

    def post(self, request, course_slug):
        cursor = connection.cursor()
        cursor.execute('select cno from courses_course where slug = %s;', [course_slug])
        cno_row = cursor.fetchone()
        cursor.close()
        if not cno_row:  # no course with this course slug (i.e. URL)
            return HttpResponseRedirect('/')  # return to main page
        cno = cno_row[0]

        form = CreateLectureForm(request.POST)

        if form.is_valid():
            lecture_name = form.cleaned_data['lecture_name']
            lecture_url = form.cleaned_data['lecture_url']

            lecture_slug = make_slug_for_url(lecture_name, for_course=False)

            cursor = connection.cursor()
            cursor.execute('INSERT INTO courses_lecture (lecture_name, lecture_slug, video_url, cno_id) VALUES '
                           '(%s, %s, %s, %s);', [lecture_name, lecture_slug, lecture_url, cno])

        warning_message = "Success: Lecture submission is successful."
        return CourseDetailView.get(self, request, warning_message)


class ChangeCourseSettingsView(View):
    template_name = "courses/course_edit.html"

    def check_validity(self, course_slug):
        cursor = connection.cursor()
        cursor.execute('select cno from courses_course where slug = %s;', [course_slug])
        cno_row = cursor.fetchone()
        if not cno_row:  # this means that the course does not exist
            return -1
        cno = cno_row[0]

        cursor.execute('select course_topic_id, topicname_id from main_course_topic where cno_id = %s;', [cno])
        course_topic_id = cursor.fetchone()

        if course_topic_id:
            course_topic_id = course_topic_id[0]

        cursor.close()

        return cno, course_topic_id

    def get(self, request, course_slug):
        if request.user.is_authenticated:  # if the user has logged in
            cno_course_topic_id = self.check_validity(course_slug)

            if cno_course_topic_id == -1:
                return HttpResponseRedirect('/')
            cno, course_topic_id = cno_course_topic_id[0], cno_course_topic_id[1]

            course = Course.objects.raw('select * from courses_course where cno = %s;', [cno])[0]
            if course.owner_id != request.user.id:
                return HttpResponseRedirect('/')

            course_form = EditCourseForm(instance=course)

            cursor = connection.cursor()
            try:
                cursor.execute('select type from auth_user where id = %s;', [request.user.id])
                user_type = cursor.fetchone()

                if user_type:
                    user_type = user_type[0]

            finally:
                cursor.close()

            cursor = connection.cursor()
            try:
                cursor.execute('select topicname from main_topic;')
                topic_list = cursor.fetchall()
            except DatabaseError:
                return HttpResponse("There was an error.<p> " + str(sys.exc_info()))
            finally:
                cursor.close()

            cursor = connection.cursor()
            cursor.execute('''SELECT U.username 
                                    FROM main_contributor AS MC,auth_user AS U
                                    WHERE MC.cno_id = %s AND MC.user_id = U.id;''', [cno])

            contributor_list = cursor.fetchall()
            contributors = [None] * len(contributor_list)
            for i in range(0, len(contributors)):
                contributors[i] = contributor_list[i][0]
                print(contributor_list[i][0])

            cursor.close()

            contributor_form = AddContributorForm()

            return render(request, self.template_name, {'course_form': course_form, 'course': course,
                                                        'user_type': user_type, 'topic_list': topic_list,
                                                        'course_slug': course_slug, 'contributors': contributors})
        return HttpResponseRedirect('/')

    def post(self, request, course_slug):
        cno_course_topic_id = self.check_validity(course_slug)

        if cno_course_topic_id == -1:
            return HttpResponseRedirect('/')
        cno, course_topic_id = cno_course_topic_id[0], cno_course_topic_id[1]
        course_form = EditCourseForm(request.POST, request.FILES,
                                     instance=Course.objects.raw('select * from courses_course where cno = %s;',
                                                                 [cno])[0])
        if course_form.is_valid():
            cname = course_form.cleaned_data['cname']
            price = course_form.cleaned_data['price']
            course_img = course_form.cleaned_data['course_img']
            description = course_form.cleaned_data['description']
            private = course_form.cleaned_data['private']

            cursor = connection.cursor()
            cursor.execute('update courses_course '
                           'set cname = %s, price = %s, course_img = %s, description = %s, is_private = %s '
                           'where cno = %s;', [cname, price, course_img, description, private, cno])
            cursor.close()

        contributor_form = AddContributorForm(request.POST)
        cursor = connection.cursor()
        if contributor_form.is_valid():
            contributor_username = contributor_form.cleaned_data['addcontributor']
            cursor.execute('SELECT id FROM auth_user WHERE username = %s;', [contributor_username])
            c_id_list = cursor.fetchone()
            if (c_id_list == None):
                cursor.close()
                return HttpResponseRedirect("/" + course_slug + "/" + edit)
            c_id = c_id_list[0];

            cursor.execute('SELECT user_id FROM main_contributor WHERE cno_id = %s and user_id = %s;', [cno, c_id])
            if not cursor.fetchone():
                cursor.execute('INSERT INTO main_contributor(cno_id, user_id) VALUES( %s, %s); ',
                               [cno, c_id])
            return HttpResponseRedirect('/' + course_slug + '/edit')

        cursor.close()
        return HttpResponseRedirect('/' + course_slug)


class DeleteContributerView(View):
    def post(self, request, course_slug, c_username, *args, **kwarg):

        cursor = connection.cursor()

        cursor.execute('select cno from courses_course where slug = %s;', [course_slug])
        cno_row = cursor.fetchone()
        if not cno_row:  # no course with this course slug (i.e. URL)
            return HttpResponseRedirect("/" + course_slug + "/" + edit)  # return to main page
        cno = cno_row[0]

        cursor.execute('SELECT id FROM auth_user WHERE username = %s;', [c_username])
        c_id_list = cursor.fetchone()
        if (c_id_list == None):
            return HttpResponseRedirect("/" + course_slug + "/" + edit)
        c_id = c_id_list[0];

        cursor.execute('DELETE FROM main_contributor WHERE cno_id = %s AND user_id = %s;', [cno, c_id])

        cursor.close()
        return HttpResponseRedirect("/" + course_slug + "/edit")


class OfferAdView(View):
    template_name = "courses/offer_ad.html"

    def get(self, request, course_slug):
        form = OfferAdForm()

        cursor = connection.cursor()
        cursor.execute('select type '
                       'from user_types '
                       'where id = %s;', [request.user.id])

        row = cursor.fetchone()
        user_type = -1
        if row:
            user_type = row[0]

        topic_list = Topic.objects.raw('select topicname from main_topic;')

        context = {'user_type': user_type,
                   'form': form,
                   'path': request.path,
                   'topic_list': topic_list,
                   }

        return render(request, self.template_name, context)

    def post(self, request, course_slug):
        form = OfferAdForm(request.POST, request.FILES)
        if form.is_valid():
            ad_img = form.cleaned_data["ad_img"]
            status = 0  # 0 for waiting, 1 for refused, 2 for accepted
            price = form.cleaned_data["price"]
            startdate = form.cleaned_data["start_date"]
            finishdate = form.cleaned_data["end_date"]

            cursor = connection.cursor()
            cursor.execute('select cno from courses_course where slug = %s;', [course_slug])
            cno_row = cursor.fetchone()
            cursor.close()
            if not cno_row:  # no course with this course slug (i.e. URL)
                return HttpResponseRedirect('/')  # return to main page
            cno = cno_row[0]

            cursor = connection.cursor()
            cursor.execute('INSERT INTO main_advertisement (advertisement, status, payment, startdate, finishdate,'
                           ' ad_username_id, cno_id) VALUES (%s, %s, %s, %s, %s, %s, %s);',
                           [ad_img, status, price, startdate, finishdate, request.user.id, cno])
            cursor.close()
        return redirect("main:offers")


def mark_as_complete(request, course_slug):
    if request.user.is_authenticated:
        # check for user type
        user_type = get_user_type(request)
        if user_type != 1:  # not an instructor
            return HttpResponseRedirect('/')
        # check if the user is the owner
        cursor = connection.cursor()
        try:
            cursor.execute('select cno, owner_id from courses_course where slug = %s;', [course_slug])
            owner_row = cursor.fetchone()
            if not owner_row:  # the course does not exist
                return HttpResponseRedirect('/')

            # checking for the owner themselves
            cno = owner_row[0]  # will be useful in the update statement below
            owner_id = owner_row[1]
            if owner_id != request.user.id:  # the user is not the owner
                return HttpResponseRedirect('/')

            # now we can finally mark the course as complete
            cursor.execute('update courses_course set is_complete = 1 where cno = %s;', [cno])
            response_str = '/' + course_slug
            return redirect(response_str)
        except Error:
            return HttpResponse("There was an error.<p> " + str(sys.exc_info()))
        finally:
            cursor.close()

    return HttpResponseRedirect('/')
