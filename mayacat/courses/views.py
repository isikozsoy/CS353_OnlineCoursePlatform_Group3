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
            'url' : '/'+course_slug+'/'+lecture_slug
            #'contributors' : contributors
            'form_lecmat_assignment': form_lecmat_assignment,
            'user_type': user_type,
        }
        cursor.close()

        form = AskQuestion()
        print(form)
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
        form = AskQuestion(request.POST)
        if form.is_valid():
            question = form.cleaned_data['question']
            print("Question : ",question)
            cursor.execute('insert into main_post (post, lecture_no_id, username_id) values (%s, %s, %s);',
                           [question,lecture_no,request.user.id])

        cursor.close()
        return HttpResponseRedirect(request.path)



class CourseFinishView(View):
    def get(self, request, course_slug, lecture_slug, *args, **kwargs):
        context = {
            'curlecture': 'CURLECTURE'
        }
        return render(request, 'courses/course_finish.html', context)

        cursor.close()
        return HttpResponseRedirect(request.path)


def send_course_as_gift(request, course_slug, receiver):
    course_queue = Course.objects.raw('SELECT * FROM courses_course as C WHERE C.slug = %s', [course_slug])
    if len(list(course_queue)) != 0:
        course = Course.objects.raw('SELECT * FROM courses_course as C WHERE C.slug = %s LIMIT 1', [course_slug])[0]
        cno = course.cno
    else:
        return

        # WILL BE CHANGED TO CURRENT USER
        s = request.user

        if not Enroll.objects.raw('SELECT * FROM main_enroll as E WHERE E.cno_id = %s AND E.user_id= %s', [cno]):
            Gift.objects.create(wishes_id=uuid.uuid1(), cno=course, user=s)
        else:
            Wishes.objects.filter(cno=course, user=s).delete()

    return redirect("courses:my_courses")


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

            return render(request, self.template_name, {'form': form,
                                                        'user_type': user_type})
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

            return render(request, self.template_name, {'form': form,
                                                        'user_type': user_type})
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

        return render(request, self.template_name, {'user_type': user_type,
                                                    'form': form,
                                                    'add_message': 'Add a course as an instructor:',
                                                    'create_button': 'Create a course!'})

    def post(self, request):
        form = CreateCourseForm(request.POST, request.FILES)

        if form.is_valid():
            cname = form.cleaned_data['cname']
            price = form.cleaned_data['price']
            topic = form.cleaned_data['topic']
            thumbnail = form.cleaned_data['course_img']

            description = form.cleaned_data['description']
            private = form.cleaned_data['private']

            orig_slug = make_slug_for_url(cname)
            cursor = connection.cursor()
            cursor.execute('INSERT INTO courses_course '
                           '(cname, price, slug, situation, is_private, course_img, description, owner_id) '
                           'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                           [cname, price, orig_slug, 'Pending', private, thumbnail, description, request.user.id])
            cno = Course.objects.raw('select * from courses_course where slug = %s;', [orig_slug])[0].cno
            cursor.close()
            cursor = connection.cursor()
            cursor.execute('INSERT INTO main_course_topic (cno_id, topicname_id) '
                           'VALUES (%s, %s);', [cno, topic])
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

        return render(request, self.template_name, {'user_type': user_type, 'form': form, 'add_message': message,
                                                    'create_button': 'Create a lecture!'})

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


def change_course_settings(request, course_slug):
    cursor = connection.cursor()
    cursor.execute('select owner_id from courses_course where slug = %s;', [course_slug])
    owner_id_row = cursor.fetchone()
    if not owner_id_row:  # meaning this course does not exist
        return HttpResponseRedirect('/')  # return to main page

    owner_id = owner_id_row[0]

    if request.user.id != owner_id:  # return to main page if the owner is not
        return HttpResponseRedirect('/' + course_slug)

    if request.method == "POST":
        return
    else:
        return HttpResponseRedirect('/' + course_slug)


class OfferAdView(View):
    template_name = "courses/offer_ad.html"

    def get(self, request, course_slug):
        cursor = connection.cursor()
        cursor.execute('select type '
                       'from auth_user '
                       'inner join accounts_defaultuser ad on auth_user.id = ad.user_ptr_id '
                       'where id = %s;', [request.user.id])

        row = cursor.fetchone()
        user_type = -1
        if row:
            user_type = row[0]

        context = {'user_type': user_type}
        print("-------------icerdeyizzzz")
        return render(request, self.template_name, context)
