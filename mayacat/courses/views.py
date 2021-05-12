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

from .forms import *

class MyCoursesView(ListView):
    def get(self, request):
        if request.user.is_authenticated:
            user_id = request.user.id
            my_courses_q = Enroll.objects.raw('''SELECT *
                                                FROM main_enroll
                                                WHERE user_id = %s''', [user_id])

            cursor = connection.cursor()
            cursor.execute('select type '
                           'from auth_user '
                           'inner join accounts_defaultuser ad on auth_user.id = ad.user_ptr_id '
                           'where id = %s;', [user_id])

            row = cursor.fetchone()
            user_type = -1
            if row:
                user_type = row[0]

            topic_list = Topic.objects.raw('select topicname from main_topic;')
            context = {
                'my_courses_q': my_courses_q,
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
    def get(self, request, course_slug):
        form = GiftInfo()
        cursor = connection.cursor()


        course = Course.objects.raw('SELECT * FROM courses_course WHERE slug = %s;', [course_slug])
        if len(list(course)) != 0:
            course = course[0]
        else:
            return HttpResponseRedirect('/')
        cno = course.cno

        lecture_list = Lecture.objects.raw('SELECT * FROM courses_lecture WHERE cno_id = %s;', [cno])

        is_owner = False
        is_only_gift = False
        is_enrolled = 0
        if course.owner_id == request.user.id:
            is_owner = True
            is_only_gift = True

        else:
            cursor.execute('SELECT count(*) FROM main_enroll as E WHERE E.cno_id = %s AND E.user_id= %s',
                                             [cno, request.user.id])
            is_enrolled = cursor.fetchone()[0]
            is_in_cart = Inside_Cart.objects.raw('SELECT * FROM main_inside_cart WHERE cno_id = %s AND username_id= %s AND '
                                                 'receiver_username_id = %s', [cno, request.user.id, request.user.id])
            if is_enrolled or is_in_cart:
                is_only_gift = True

        lecture_list = Lecture.objects.raw('SELECT * FROM courses_lecture WHERE cno_id = %s;', [cno])
        cursor.execute('SELECT * FROM courses_lecture WHERE cno_id = %s;', [cno])

        lecture_list = cursor.fetchone()

        if lecture_list:
            lecture_list = cursor.fetchone()[0]

        is_wish = len(list(Wishes.objects.raw('SELECT * FROM main_wishes WHERE cno_id = %s AND user_id = %s;',
                                              [cno, request.user.id])))

        registered = len(list(Enroll.objects.raw('SELECT * FROM main_enroll WHERE cno_id = %s AND user_id = %s;',
                                                  [cno, request.user.id])))

        lectures = Lecture.objects.raw('''SELECT * FROM courses_lecture as CL WHERE CL.cno_id = %s;''', [cno])
        lecture_count = len(lectures)

        cursor.execute('SELECT AVG(score) FROM main_finishes WHERE cno_id = %s AND score !=0', [cno])
        rating = cursor.fetchone()[0]
        print("Rating:",rating)

        cursor.execute('SELECT * '
                       'FROM main_advertisement '
                       'WHERE cno_id = %s AND status = 1 '
                       'AND (CURRENT_TIMESTAMP BETWEEN startdate AND finishdate) ',[cno])

        advertisement_list = cursor.fetchone()
        print("advertisement",advertisement_list)

        advertisement = {
            'advertisement' : advertisement_list[1],
            'ad_username_id': advertisement_list[6],
            'startdate' : advertisement_list[4]
        }


        cursor.execute('SELECT comment FROM main_finishes WHERE cno_id = %s;', [cno])

        comment_list = cursor.fetchall()
        comments = [None]*len(comment_list)
        for i in range(0,len(comment_list)):
            comments[i] = comment_list[i][0]

        cursor.execute('select type '
                       'from auth_user '
                       'inner join accounts_defaultuser ad on auth_user.id = ad.user_ptr_id '
                       'where id = %s;', [request.user.id])

        row = cursor.fetchone()
        user_type = -1
        if row:
            user_type = row[0]
        cursor.execute('SELECT count(*) '
                       'FROM main_wishes WHERE cno_id = %s AND user_id = %s;',
                                              [cno, request.user.id])
        is_wish = cursor.fetchone()[0]

        topic_list = Topic.objects.raw('select topicname from main_topic;')
        discounted_price = course.price


        today = date.today()
        print("Today:",today)

        cursor.execute('''SELECT * FROM main_discount AS MD 
                            WHERE MD.cno_id = %s AND (CURRENT_TIMESTAMP BETWEEN MD.startdate AND MD.finishdate) 
                                AND MD.situation = 1 ;''',
                                   [course.cno])
        discounts = cursor.fetchall()
        print("Discount: ",discounts)
        if(len(discounts)>0):
            print("NEW PRICE",discounts[0][2])
            discounted_price = discounts[0][2]

        context = {
            'lecture_list': lecture_list,
            'form': form,
            'course': course,
            'is_wish': is_wish,
            'user_type': user_type,
            'path': request.path,
            'is_gift': is_only_gift,
            'topic_list': topic_list,
            'registered': registered,
            'user_type': user_type,
            'lecture_count': lecture_count,
            'rating': rating,
            'advertisement': advertisement,
            'comments': comments,
            'discounted_price' : discounted_price,
            'is_gift': is_only_gift,
            'is_owner': is_owner,
            'is_enrolled': is_enrolled
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
                               'VALUES (%s, %s, %s);', [cno, request.user.id, request.user.id])  # own id if it is not a gift
                cursor.close()
                return redirect("main:cart")

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

    def get(self, request, course_slug, lecture_slug,question_no, *args, **kwargs):
        answer = "to be completed"
        form = AnswerQuestion()
        context = {
            'question_no' : question_no,
            'answer' : answer
        }
        return render(request, 'courses/add_answer.html', context)
    def post(self, request, course_slug, lecture_slug,question_no, *args, **kwargs):
        form = AnswerQuestion(request.POST)
        cursor = connection.cursor()
        if form.is_valid():
            answer = form.cleaned_data['answer']
        print("course_slug",course_slug,"lecture_slug",lecture_slug,"question_no ",question_no)
        cursor.execute('select lecture_no from courses_lecture where lecture_slug = %s;', [lecture_slug])
        lecture_no_row = cursor.fetchone()
        cursor.close()
        if not lecture_no_row:
            return HttpResponseRedirect('/')
        cursor = connection.cursor()

        lecture_no = lecture_no_row[0]
        cursor.execute('insert into main_post (post, lecture_no_id, username_id) values (%s, %s, %s);',
                       [answer, lecture_no, request.user.id])
        cursor.execute('select LAST_INSERT_ID()')
        row = cursor.fetchone()
        print("row",row)
        if row:
            ans_no = row[0]
            print("In post of addanswerview",ans_no)
            cursor.execute('insert into main_quest_answ (answer_no_id, question_no_id) values (%s, %s);',
                           [ans_no, question_no])
        cursor.close()
        return HttpResponseRedirect("/"+course_slug+"/"+lecture_slug)


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
        isFinished = 0
        if (len(isWatched) == 0):
            cursor.execute('''INSERT INTO main_progress(lecture_no_id ,s_username_id) VALUES (%s, %s); ''',
                       [lecture.lecture_no, curuser_id])
            prog = Progress.objects.raw( '''SELECT MP.prog_id FROM main_progress as MP
                                            WHERE MP.s_username_id = %s AND 
                                                  MP.lecture_no_id IN ( SELECT lecture_no
                                                                        FROM courses_lecture 
                                                                        WHERE cno_id = %s );'''
                                              ,[curuser_id,cno])
            print("prog : ", len(prog))     #raw must include primary key - cursor
            if (len(prog) == len(lectures)):
                print("course finished")
                cursor.execute('''INSERT INTO main_finishes(comment,cno_id,user_id,score) VALUES (%s,%s, %s,%s);''',
                                  ["",cno,curuser_id,0])
        prog = Progress.objects.raw('''SELECT MP.prog_id FROM main_progress as MP
                                                    WHERE MP.s_username_id = %s AND 
                                                          MP.lecture_no_id IN ( SELECT lecture_no
                                                                                FROM courses_lecture 
                                                                                WHERE cno_id = %s );'''
                                    , [curuser_id, cno])
        if (len(prog) == len(lectures)):
            print("This course is finished")
            isFinished = 1

        print("- ", cno)

        # lectures = Lecture.objects.raw('''SELECT * FROM courses_lecture;''')
        print("=6", lecture_slug, course.cno, lectures, len(lectures))

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


        announcements = Announcement.objects.raw('''SELECT * FROM main_announcement as MA,auth_user as U 
                                                    WHERE MA.cno_id = %s and MA.i_user_id = U.id;''', [cno])
        #announcements = Announcement.objects.filter(cno_id=course.cno)

        notes = Takes_note.objects.raw( '''SELECT * FROM main_takes_note as MTN 
                                            WHERE MTN.lecture_no_id = %s AND MTN.s_username_id = %s;''',
                                            [lecture.lecture_no, curuser_id])
        newNote = NewNoteForm()
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

        cursor.execute('''SELECT U.username 
                        FROM main_contributor AS MC,auth_user AS U
                        WHERE MC.cno_id = %s AND MC.user_id = U.id;''',[course.cno])

        contributor_list = cursor.fetchall()
        contributors = [None]*len(contributor_list)
        for i in range(0,len(contributors)):
            contributors[i] = contributor_list[i][0]
            print(contributor_list[i][0])
        print("Contributors:",contributors)

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
                       'from auth_user '
                       'inner join accounts_defaultuser ad on auth_user.id = ad.user_ptr_id '
                       'where id = %s;', [request.user.id])

        row = cursor.fetchone()
        user_type = -1
        if row:
            user_type = row[0]

        form_question = AskQuestion()
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
            'qanda' : qanda,
            'lecandprog' : lecandprog,
            'url' : '/'+course_slug+'/'+lecture_slug,
            'contributors' : contributors,
            'form_lecmat_assignment': form_lecmat_assignment,
            'user_type': user_type,
            'topic_list': topic_list,
            'isFinished' : isFinished,
            'teaches' : teaches
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
            return HttpResponseRedirect('/')

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


        form_note = NewNoteForm(request.POST)
        if form_note.is_valid():
            newnote = form_note.cleaned_data['note']
            cursor.execute( 'INSERT INTO main_takes_note(note,lecture_no_id, s_username_id ) VALUES(%s,%s,%s);',
                            [newnote, lecture_no,request.user.id ])

        form_question = AskQuestion(request.POST)
        if form_question.is_valid():
            question = form_question.cleaned_data['question']
            print("Question : ",question)
            cursor.execute('insert into main_post (post, lecture_no_id, username_id) values (%s, %s, %s);',
                           [question,lecture_no,request.user.id])

        cursor.close()
        return HttpResponseRedirect(request.path)


class CourseFinishView(View):
    def get(self, request, course_slug, *args, **kwargs):
        cursor = connections['default'].cursor()

        course_queue = Course.objects.raw('''SELECT * FROM courses_course WHERE slug = %s;''', [course_slug])

        curuser_id = request.user.id
        print(curuser_id)

        if len(course_queue) > 0:
            course = course_queue[0]
        else:
            # 404 error
            print("error no course as the stated");

        finish_list = Finishes.objects.raw('''SELECT * FROM main_finishes as MF WHERE MF.cno_id = %s AND MF.user_id = %s;''',
                                        [course.cno, curuser_id])
        currate = finish_list[0].score
        curcomment = finish_list[0].comment


        comment = FinishCourseCommentForm()
        rate = FinishCourseRateForm()

        cursor.execute('select type '
                       'from auth_user '
                       'inner join accounts_defaultuser ad on auth_user.id = ad.user_ptr_id '
                       'where id = %s;', [request.user.id])

        row = cursor.fetchone()
        user_type = -1
        if row:
            user_type = row[0]
        context = {
            'currate' : currate,
            'curcomment' : curcomment,
            'url' : '/'+course_slug+'/finish',
            'curcourse': course,
            'user' : curuser_id,
            'user_type': user_type
        }
        cursor.close()
        return render(request, 'courses/coursefinish.html', context)

    def post(self, request, course_slug, *args, **kwargs):
        cursor = connection.cursor()

        #cursor.execute('select lecture_no from courses_lecture where lecture_slug = %s;', [lecture_slug])
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
                           [comment,course.cno,curuser_id])

        form_rate = FinishCourseRateForm(request.POST)

        if form_rate.is_valid():
            rate = form_rate.cleaned_data['rate']
            print("Rate: ", rate)
            cursor.execute('UPDATE main_finishes SET score = %s where cno_id = %s AND user_id = %s;',
                           [int(rate), course.cno, curuser_id])
        cursor.close()
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
                           'from auth_user '
                           'inner join accounts_defaultuser ad on auth_user.id = ad.user_ptr_id '
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
                           'from auth_user '
                           'inner join accounts_defaultuser ad on auth_user.id = ad.user_ptr_id '
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
        count = cursor.fetchone()[0]
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
        is_instructor = cursor.fetchone()[0]
        cursor.close()

        if is_instructor == 0:  # this means that there is no instructor with the requested id
            return HttpResponseRedirect('/')  # TODO: A page to transform student into instructor

        form = CreateCourseForm()

        cursor = connection.cursor()
        cursor.execute('select type '
                       'from auth_user '
                       'inner join accounts_defaultuser ad on auth_user.id = ad.user_ptr_id '
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
                cursor.execute('insert into courses_course (cname, price, slug, situation, is_private, course_img, '
                               'description, owner_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);',
                               [cname, price, orig_slug, 0, private, thumbnail, description, request.user.id])
            finally:
                cursor.close()

            cursor = connection.cursor()
            try:
                cursor.execute('select cno from courses_course where cname = %s;', [cname])
                cno = cursor.fetchone()[0]
                for topic in topics:
                    cursor.execute('insert into main_course_topic (cno_id, topicname_id) VALUES (%s, %s);',
                                   [cno, topic])
            except Error:
                return HttpResponse('There was an error.')
            finally:
                cursor.close()

            messages.success(request, 'Course submission successful')
        return HttpResponseRedirect(request.path)


class AddLectureToCourseView(View):
    template_name = "courses/add_course.html"

    def get(self, request, course_slug):
        cursor = connection.cursor()
        cursor.execute('select owner_id, cname from courses_course where slug = %s;', [course_slug])
        cno_row = cursor.fetchone()
        cursor.close()
        if not cno_row:  # no course with this course slug (i.e. URL)
            return HttpResponseRedirect('/')  # return to main page

        owner_id = cno_row[0]
        cname = cno_row[1]
        # if the owner is not the user logging in, return to main page
        if request.user.id != owner_id:
            return HttpResponseRedirect('/')

        message = 'Add a lecture to ' + cname

        form = CreateLectureForm()

        cursor = connection.cursor()
        cursor.execute('select type '
                       'from auth_user '
                       'inner join accounts_defaultuser ad on auth_user.id = ad.user_ptr_id '
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
            messages.success(request, 'Lecture submission successful')

        return HttpResponseRedirect(request.path)


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
        course_topic_id = cursor.fetchone()[0]

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
                cursor.execute('select type from accounts_defaultuser where user_ptr_id = %s;', [request.user.id])
                user_type = cursor.fetchone()[0]
            finally:
                cursor.close()

            cursor = connection.cursor()
            try:
                cursor.execute('select topicname from main_topic;')
                topic_list = cursor.fetchall()
            except DatabaseError:
                return HttpResponse('There was an error.')
            finally:
                cursor.close()

            return render(request, self.template_name, {'course_form': course_form, 'course': course,
                                                        'user_type': user_type, 'topic_list': topic_list, })
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

        return HttpResponseRedirect('/' + course_slug)


class OfferAdView(View):
    template_name = "courses/offer_ad.html"

    def get(self, request, course_slug):
        form = OfferAdForm()

        cursor = connection.cursor()
        cursor.execute('select type '
                       'from auth_user '
                       'inner join accounts_defaultuser ad on auth_user.id = ad.user_ptr_id '
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
