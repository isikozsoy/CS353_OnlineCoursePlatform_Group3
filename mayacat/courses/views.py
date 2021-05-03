import datetime
from .forms import *
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import ListView, DetailView
from django.views.generic.base import View
from django.db import connection
from main.models import *
from accounts.models import *
from .models import *
from slugify import slugify

cursor = connection.cursor()


def get_today():
    return datetime.datetime.now().strftime('%y-%m-%d')


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


def add_to_my_courses(request, course_slug):
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
    return HttpResponseRedirect('/my_courses/add/')


class CourseListView(ListView):
    model = Course


class CourseDetailView(View):
    # model = Course

    def get(self, request, course_slug):
        form = GiftInfo()

        course_queue = Course.objects.raw('SELECT * FROM courses_course WHERE slug = %s', [course_slug])
        if len(list(course_queue)) != 0:
            course = Course.objects.raw('SELECT * FROM courses_course WHERE slug = %s LIMIT 1', [course_slug])[
                0]
            cno = course.cno
        else:
            return

        lecture_list = Lecture.objects.raw('SELECT * FROM courses_lecture WHERE cno_id = %s;', [cno])
        context = {
            'lecture_list': lecture_list,
            'form': form,
            'object': course
        }
        return render(request, 'course_detail.html', context)

    def post(self, request, course_slug):
        form = GiftInfo(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            users = Student.objects.raw('SELECT * '
                                        'FROM accounts_student '
                                        'INNER JOIN auth_user '
                                        'ON defaultuser_ptr_id = id '
                                        'WHERE username = %s;',
                                        [username])
            if len(list(users)) == 0:
                pass
                # INVALID USER
            else:
                receiver_id = users[0].user_id
                course_queue = Course.objects.raw('SELECT * '
                                                  'FROM courses_course '
                                                  'WHERE slug = %s', [course_slug])
                if len(list(course_queue)) != 0:
                    course = Course.objects.raw('SELECT * '
                                                'FROM courses_course '
                                                'WHERE slug = %s LIMIT 1', [course_slug])[0]
                    cno = course.cno
                else:
                    return

                cursor.execute('INSERT INTO main_gift (sender_id, receiver_id, course_id, date) VALUES (%s, %s);',
                               [request.user.id, receiver_id, cno, get_today()])
                cursor.execute('INSERT INTO main_enroll (cno_id, user_id) VALUES (%s, %s);',
                               [cno, receiver_id])
                return HttpResponseRedirect('my_courses')

        return HttpResponse("Invalid input. Go back and try again...")


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

        return render(request, 'main/lecture_detail.html', context)


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


class AddComplainView(View):
    template_name = "main/complain.html"
    course_slug = ""

    def get(self, request, course_slug):
        form = ComplainForm()
        self.course_slug = course_slug
        if request.user.is_authenticated:  # we need to check enrollments as well
            return render(request, self.template_name, {'form': form})
        return HttpResponseRedirect('/')

    def post(self, request, course_slug):
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
            render(request, "trivial/success_message_after_submitting.html",
                   {'success_message': 'Your refund request has been sent to the administrators. '
                                       'You will get an answer in approximately a week. Please be patient.',
                    'course_slug': course_slug})
        else:
            print("Invalid form")
        return HttpResponseRedirect('/')


class RefundRequestView(View):
    template_name = "main/refund.html"
    course_slug = ""

    def get(self, request, course_slug):
        form = ComplainForm()
        self.course_slug = course_slug
        if request.user.is_authenticated:  # we need to check enrollments as well
            return render(request, self.template_name, {'form': form})
        return HttpResponseRedirect('/')

    def post(self, request, course_slug):
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
            return render(request, "trivial/success_message_after_submitting.html",
                          {'success_message': 'Your refund request has been sent to the administrators. '
                                              'You will get an answer in approximately a week. Please be patient.',
                           'course_slug': course_slug})
        else:
            print("Invalid form")
        return HttpResponseRedirect('/')


class AddCourseView(View):
    template_name = "courses/add_course.html"

    def get(self, request):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/')

        cursor.execute('select count(*) '
                       'from accounts_instructor '
                       'where student_ptr_id = %s;', [request.user.id])
        is_instructor = cursor.fetchone()[0]

        if is_instructor == 0:  # this means that there is no instructor with the requested id
            return HttpResponseRedirect('/')  # TODO: A page to transform student into instructor

        form = CreateCourseForm()

        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CreateCourseForm(request.POST, request.FILES)

        if form.is_valid():
            cname = form.cleaned_data['cname']
            price = form.cleaned_data['price']
            topic = form.cleaned_data['topic']
            thumbnail = form.cleaned_data['course_img']

            description = form.cleaned_data['description']
            private = form.cleaned_data['private']

            # TODO:
            # TODO: SLUG = CNO YU YAPSAK ÇOK GÜZEL OLUR AMA TABLE'DA CNO KURSU YERLEŞTİRDİKTEN SONRA OLUŞUYOR
            # TODO: BUNU YAPMANIN BİR YÖNTEMİ ŞÖYLE: COURSES'I SİLİYORUZ, İÇİNDE SLUG'IN REQUIRED OLMADIĞI BİR TABLE
            #  OLUŞTURUYORUZ, SONRA CNO cursor.execute İLE OLUŞUNCA TEKRAR CNO'YU BU TABLE'DAN ÇEKİP UPDATE KOMUTU İLE
            #  SLUG'I GÜNCELLİYORUZ
            orig_slug = slugify(cname)

            # check for the existence of the same slug below so that the slug is unique
            unique = False
            uniquifier = 1
            slug = orig_slug
            while not unique:
                cursor.execute('select count(*) from courses_course where slug = %s;', [slug])
                count = cursor.fetchone()[0]
                if count != 0:
                    orig_slug = slug + '-' + str(uniquifier)
                    uniquifier += 1
                else:
                    unique = True

            cursor.execute('INSERT INTO courses_course '
                           '(cname, price, slug, situation, is_private, course_img, description, owner_id) '
                           'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                           [cname, price, orig_slug, 'Pending', private, thumbnail, description, request.user.id])
            cno = Course.objects.raw('select * from courses_course where slug = %s;', [slug])[0].cno
            cursor.execute('INSERT INTO main_course_topic (cno_id, topicname_id) '
                           'VALUES (%s, %s);', [cno, topic])

            return HttpResponse("Course addition successful. The decision on course will be made in approximately a "
                                "week. Please be patient.")

        return HttpResponseRedirect('/')


class RateView(View):
    template_name = "courses/evaluate.html"

    def get(self, request, course_slug):
        if request.user.is_authenticated:
            # check if the user is a student
            cursor.execute('select * from accounts_student where defaultuser_ptr_id = %s;', [request.user.id])
            student_check_row = cursor.fetchone()
            if not student_check_row:  # if a student like this does not exist, return to main page
                return HttpResponseRedirect('/')

            # check for a course with the parameter course_slug
            cursor.execute('select cno from courses_course where slug = %s;', [course_slug])
            cno_row = cursor.fetchone()

            if not cno_row:  # if a course like this does not exist, return to main page
                return HttpResponseRedirect('/')

            cno = cno_row[0] # course exists

            # check if the user is enrolled
            cursor.execute('select * from main_enroll where cno_id = %s and user_id = %s;', [cno, request.user.id])
            enroll_row = cursor.fetchone()

            if not enroll_row:  # return to main page if not enrolled in the course
                return HttpResponseRedirect('/')

            return render(request, self.template_name) # now the user can evaluate the course

        return HttpResponseRedirect('/')
