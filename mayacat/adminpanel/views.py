import sys

from django.contrib.auth.models import User
from django.db import Error, DatabaseError
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from datetime import date

# Create your views here.
from django.views.generic import View

from .forms import *
from courses.views import make_slug_for_url


class AdminMainView(View):
    template_name = "adminpanel/admin_main.html"

    def get(self, request):
        if request.method == 'GET' and request.user.is_authenticated and request.user.is_superuser:
            discount_form = DiscountForm()

            return render(request, self.template_name, {'discount_form': discount_form})
        return HttpResponseRedirect('/')


def create_discount(request):
    if request.method == 'POST' and request.user.is_authenticated and request.user.is_superuser:
        discount_form = DiscountForm(request.POST)

        if discount_form.is_valid():
            start_date = discount_form.cleaned_data['start_date']
            end_date = discount_form.cleaned_data['end_date']
            percentage = discount_form.cleaned_data['percentage']

            cursor = connection.cursor()
            try:
                cursor.execute('insert into adminpanel_offered_discount '
                               '(creation_date, percentage, start_date, end_date, admin_username_id) '
                               'values (curdate(), %s, %s, %s, %s);',
                               [percentage, start_date, end_date, request.user.id])
            except Error:
                return HttpResponse("There was an error.<p> " + str(sys.exc_info()))
            finally:
                cursor.close()
        else:
            print(discount_form.errors)
        return redirect('adminpanel:admin_main')
    return HttpResponseRedirect('/login')


class AdminRefundView(View):
    template_name = "adminpanel/admin_refund.html"

    # Main view page of admin will list refunds waiting for a decision, add those refunds to evaluated,
    # and also create new instances of discounts if the admin wants so
    # The decision on these discounts will then be handed over to instructors for their respective courses.
    def get(self, request):
        if request.method == 'GET' and request.user.is_authenticated and request.user.is_superuser:
            cursor = connection.cursor()
            try:  # status = 0 are refunds that are pending for a decision
                cursor.execute('select refund_id, reason, status, cno_id, s_username_id, date '
                               'from main_refundrequest '
                               'where status = 0 order by date;')
                refund_set = cursor.fetchall()

                cursor = connection.cursor()
                try:
                    cursor.execute('select topicname from main_topic;')
                    topic_list = cursor.fetchall()
                except DatabaseError:
                    return HttpResponse("There was an error.<p> " + str(sys.exc_info()))
                finally:
                    cursor.close()

                return render(request, self.template_name, {'refunds': refund_set,
                                                            'user_type': 3,
                                                            'topic_list': topic_list}, )
            except Error:
                return HttpResponse("There was an error.<p> " + str(sys.exc_info()))
            finally:
                cursor.close()
        return HttpResponseRedirect('/logout')


def accept_refund(request, refund_id, accepted):
    if request.method == 'POST' and request.user.is_authenticated and request.user.is_superuser:
        status = -1
        if accepted == 'True':
            status = 1

        cursor = connection.cursor()
        try:
            cursor.execute('update main_refundrequest set status = %s where refund_id = %s;', [status, refund_id])
            cursor.execute('insert into main_evaluates (refund_id_id, reply_date, admin_username_id) '
                           'values (%s, %s, %s);', [refund_id, date.today(), request.user.id])
        except Error:
            return HttpResponse("There was an error.<p> " + str(sys.exc_info()))
        finally:
            cursor.close()
        return redirect('adminpanel:admin_main')
    return HttpResponseRedirect('/')


def dateDiff(date1):
    today = date.today()
    return abs((date1 - today).days)


class AdminFirstRegisterView(View):
    template_name = "adminpanel/register.html"

    def get(self, request):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return HttpResponseRedirect('/')
        # also check if the user needs to refresh their ssn and address
        cursor = connection.cursor()
        try:
            cursor.execute('select * from accounts_defaultuser where user_ptr_id = %s;', [request.user.id])
            result_user = cursor.fetchall()
            if result_user:  # meaning the user has previously been saved as an admin
                return redirect('adminpanel:admin_main')
        finally:
            cursor.close()
        # ask for ssn and address
        admin_save_form = SiteAdminSaveForm()

        topic_list = Topic.objects.raw('select * from main_topic order by topicname;')

        return render(request, self.template_name, {'admin_save_form': admin_save_form,
                                                    'user_type': 3,
                                                    'topic_list': topic_list})

    def post(self, request):
        admin_save_form = SiteAdminSaveForm(request.POST)
        cursor = connection.cursor()
        if admin_save_form.is_valid():
            print("Valid form for admin register")
            ssn = admin_save_form.cleaned_data['ssn']
            address = admin_save_form.cleaned_data['address']
            cursor.execute(
                'insert into accounts_defaultuser (user_ptr_id, password_orig, type) '  # password orig will be  
                # stored as empty for admins
                'values (%s, %s, %s);', [request.user.id, "0", 3])
            cursor.execute('insert into accounts_siteadmin (defaultuser_ptr_id, ssn, address) '
                           'values (%s, %s, %s);', [request.user.id, ssn, address])
            cursor.close()
        print(admin_save_form.errors)
        return HttpResponseRedirect('/admin')


class AdminCreateView(View):  # this page is '/admin'
    template_name = "adminpanel/admin_create.html"

    def get(self, request):
        # first all the evaluations to be done are listed
        if not request.user.is_superuser:
            return HttpResponseRedirect('/')

        self.save_as_siteadmin(request.user.id)

        form_user = UserCreate()
        form_instructor = InstructorCreate()
        form_advertiser = AdvertiserCreate()
        form_siteadmin = SiteAdminCreate()
        form_course = CourseCreate()
        form_lecture = LectureCreate()

        return render(request, self.template_name, {'form_user': form_user,
                                                    'form_instructor': form_instructor,
                                                    'form_advertiser': form_advertiser,
                                                    'form_siteadmin': form_siteadmin,
                                                    'form_course': form_course,
                                                    'form_lecture': form_lecture,
                                                    'user_type': 3, })

    def post(self, request):
        form_user = UserCreate(request.POST)
        form_instructor = InstructorCreate(request.POST)
        form_advertiser = AdvertiserCreate(request.POST)
        form_siteadmin = SiteAdminCreate(request.POST)

        if form_user.is_valid():
            username = form_user.cleaned_data['username']
            email = form_user.cleaned_data['email']
            phone = form_user.cleaned_data['phone']
            password = form_user.cleaned_data['password']

            new_user = User(username=username, email=email, password=password)
            new_user.save()
            cursor = connection.cursor()

            cursor.execute('select id from auth_user where username = %s;', [username])
            new_user_id = cursor.fetchone()[0]
        else:
            return HttpResponseRedirect('/admin')

        if "student_create" in request.POST:
            cursor.execute('insert into accounts_defaultuser (user_ptr_id, password_orig, type) VALUES (%s, %s, %s);',
                           [new_user_id, password, 0])
            cursor.execute('insert into accounts_student (defaultuser_ptr_id, phone) VALUES (%s, %s);',
                           [new_user_id, phone])
        elif "instructor_create" in request.POST:
            if form_instructor.is_valid():
                cursor.execute(
                    'insert into accounts_defaultuser (user_ptr_id, password_orig, type) VALUES (%s, %s, %s);',
                    [new_user_id, password, 1])
                cursor.execute('insert into accounts_student (defaultuser_ptr_id, phone) VALUES (%s, %s);',
                               [new_user_id, phone])
                description = form_instructor.cleaned_data['description']
                cursor.execute('insert into accounts_instructor (student_ptr_id, description) VALUES (%s, %s);',
                               [new_user_id, description])
            else:
                return HttpResponseRedirect('/admin')
        elif "advertiser_create" in request.POST:
            if form_advertiser.is_valid():
                name = form_advertiser.cleaned_data['name']
                company_name = form_advertiser.cleaned_data['company_name']
                cursor.execute(
                    'insert into accounts_defaultuser (user_ptr_id, password_orig, type) VALUES (%s, %s, %s);',
                    [new_user_id, password, 2])
                cursor.execute('insert into accounts_advertiser (defaultuser_ptr_id, name, company_name, '
                               'phone) VALUES (%s, %s, %s, %s);',
                               [new_user_id, name, company_name, phone])
            else:
                return HttpResponseRedirect('/admin')
        elif "siteadmin_create" in request.POST:
            if form_siteadmin.is_valid():
                address = form_siteadmin.cleaned_data['address']
                ssn = form_siteadmin.cleaned_data['ssn']

                admin_user = User.objects.raw('select * from auth_user where username = %s;', [username])[0]
                admin_user.set_password(password)
                admin_user.save()

                cursor.execute('update auth_user set is_superuser = 1 where username = %s;', [username])
                cursor.execute(
                    'insert into accounts_defaultuser (user_ptr_id, password_orig, type) VALUES (%s, %s, %s);',
                    [new_user_id, password, 3])
                cursor.execute('insert into accounts_siteadmin (defaultuser_ptr_id, ssn, address) VALUES (%s, %s, %s);',
                               [new_user_id, ssn, address])
            else:
                return redirect('adminpanel:admin_main')

        cursor.close()

        return redirect('adminpanel:admin_create')

    def save_as_siteadmin(self, user_id):
        cursor = connection.cursor()
        cursor.execute('select user_ptr_id from accounts_defaultuser where user_ptr_id = %s;', [user_id])
        selected = cursor.fetchall()
        cursor.close()
        if not selected:  # if the user is not officially saved
            return HttpResponseRedirect('/admin/register')


def create_lecture(request):
    if request.method == 'POST' and request.user.is_authenticated and request.user.is_superuser:
        form_lecture = LectureCreate(request.POST)
        if form_lecture.is_valid():
            video_url = form_lecture.cleaned_data['video_url']
            lecture_name = form_lecture.cleaned_data['lecture_name']
            lecture_slug = make_slug_for_url(lecture_name)
            course_name = form_lecture.cleaned_data['course']

            # get cno from course_name
            cursor = connection.cursor()
            try:
                cursor.execute('select cno from courses_course where cname = %s', [course_name])
                cno = cursor.fetchone()[0]
            finally:
                cursor.close()

            cursor = connection.cursor()
            try:
                cursor.execute('insert into courses_lecture (lecture_name, lecture_slug, video_url, cno_id) '
                               'VALUES (%s, %s, %s, %s);', [lecture_name, lecture_slug, video_url, cno])
            finally:
                cursor.close()
        print(form_lecture.errors)
    return HttpResponseRedirect('/')


def save_courses(request):
    if request.method == 'POST' and request.user.is_authenticated and request.user.is_superuser:
        form_course = CourseCreate(request.POST, request.FILES)
        cursor = connection.cursor()
        if form_course.is_valid() and "course_create" in request.POST:
            owner_username = form_course.cleaned_data['owner']
            course_img = form_course.cleaned_data['course_img']
            cname = form_course.cleaned_data['cname']
            price = form_course.cleaned_data['price']
            topics = form_course.cleaned_data.get('topic')
            description = form_course.cleaned_data['description']
            private = form_course.cleaned_data['private']

            # get owner id
            try:
                cursor.execute('select id from auth_user where username = %s;', [owner_username])
                owner_id = cursor.fetchone()[0]
            finally:
                cursor.close()

            slug = make_slug_for_url(cname)

            cursor = connection.cursor()
            try:
                cursor.execute('insert into courses_course (cname, price, slug, situation, is_private, course_img, '
                               'description, owner_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);',
                               [cname, price, slug, 0, private, course_img, description, owner_id])
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
                return HttpResponse("There was an error.<p> " + str(sys.exc_info()))
            finally:
                cursor.close()
        print(form_course.errors)
        cursor.close()
    return redirect('adminpanel:admin_create')
