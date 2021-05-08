from django.db import connection
from django.shortcuts import render, redirect
from django.views.generic.base import View, HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, logout

from .forms import *
from .models import DefaultUser, Student, Instructor, SiteAdmin, Advertiser
from main.models import *


class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect('/')


class LoginView(View):
    template_name = "login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return HttpResponseRedirect('/')

        form = Login()
        return render(request, self.template_name, {'form': form})

    def authenticate(self, request, username, password):
        query = 'select * ' \
                'from accounts_defaultuser ' \
                'inner join auth_user ' \
                'on auth_user.id = accounts_defaultuser.user_ptr_id ' \
                'where username = "' + username + '" and password_orig="' + password + '";'
        user_q = User.objects.raw(query)
        return user_q

    def post(self, request):
        form = Login(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user_qset = self.authenticate(request, username=username, password=password)

            if user_qset:
                user = user_qset[0]
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                return HttpResponseRedirect('login')


class RegisterView(View):
    template_name = "register.html"

    def get(self, request):
        if request.user.is_authenticated:
            print('Already logged in. Redirecting to the main page...')
            print(request.user)
            return HttpResponseRedirect('/')
        form = Register()

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
                                                    'path': request.path,
                                                    'user_type': user_type})

    def exists(self, username):
        query = 'select * from auth_user where username = "' + username + '";'
        user_q = User.objects.raw(query)

        if user_q:
            return True
        return False

    def post(self, request):
        form = Register(request.POST)
        cursor = connection.cursor()
        if form.is_valid():
            # Get the form values for the new user
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']

            # if the user already exists, return to the original registration page
            if self.exists(username):
                return HttpResponseRedirect('/register')

            # we first create a new User object inside the auth.models.User model
            new_user = User(username=username, email=email, password=password)
            new_user.save()

            # Then we go on to add this model to the corresponding submodels, i.e. DefaultUser where password_orig
            #  will be saved, Student, Instructor, Advertiser, etc. For this, we need the id of the user that we added
            #  previously.

            # The registration type is determined from the path the user takes for the account
            if "advertiser" in request.path:
                name = form.cleaned_data['name']
                company_name = form.cleaned_data['company_name']

                cursor.execute(
                    "insert into accounts_defaultuser(user_ptr_id, password_orig, type) values ( %s, %s, %s)",
                    [new_user.id, password, 2])
                cursor.close()
                cursor = connection.cursor()
                cursor.execute(
                    "insert into accounts_advertiser(defaultuser_ptr_id, name, company_name, phone) "
                    "values ( %s, %s, %s, %s)",
                    [new_user.id, name, company_name, phone])
            elif "instructor" in request.path:
                description = form.cleaned_data['description']

                cursor.execute(
                    "insert into accounts_defaultuser(user_ptr_id, password_orig, type) values ( %s, %s, %s)",
                    [new_user.id, password, 1])
                cursor.close()
                cursor = connection.cursor()
                cursor.execute(
                    "insert into accounts_student(defaultuser_ptr_id, phone) values ( %s, %s)",
                    [new_user.id, phone])
                cursor.close()
                cursor = connection.cursor()
                cursor.execute(
                    "insert into accounts_instructor(student_ptr_id, description) values ( %s, %s, %s)",
                    [new_user.id, description])
            else:
                cursor.execute(
                    "insert into accounts_defaultuser(user_ptr_id, password_orig, type) values ( %s, %s, %s)",
                    [new_user.id, password, 0])
                cursor.close()
                cursor = connection.cursor()
                cursor.execute(
                    "insert into accounts_student(defaultuser_ptr_id, phone, description) values ( %s, %s, %s)",
                    [new_user.id, phone, ""])

            cursor.close()

            new_user.save()
            return HttpResponseRedirect('/login')  # /login
        else:
            print("Wrong form values")
        return HttpResponse('This is Register view.')


class UserView(View):
    template_name = "account.html"

    def get(self, request, username):
        cursor = connection.cursor()
        cursor.execute('select id from auth_user where username = %s;', [username])
        user_id_row = cursor.fetchone()
        cursor.close()

        if not user_id_row:  # this means that the user with the username does not exist
            return HttpResponseRedirect('/')  # redirect to the main page

        user_id = user_id_row[0]

        if request.user.is_authenticated and request.user.id == user_id:
            return HttpResponseRedirect('/account')

        # now we need to get the user type
        cursor = connection.cursor()

        # find the type of the user
        cursor.execute('select type '
                       'from accounts_defaultuser '
                       'where user_ptr_id = %s;', [user_id])
        user_type = cursor.fetchone()[0]
        cursor.close()

        form = None

        if user_type == 0:  # it is a Student account
            user = Student.objects.raw('select * from accounts_student where defaultuser_ptr_id = %s;',
                                       [user_id])[0]
            form = StudentEditForm(instance=user, readonly=True)
        elif user_type == 1:  # it is an Instructor account
            user = Instructor.objects.raw('select * from accounts_instructor where student_ptr_id = %s;',
                                          [user_id])[0]
            form = InstructorEditForm(instance=user, readonly=True)
        elif user_type == 2:  # advertiser account
            user = Advertiser.objects.raw('select * from accounts_advertiser where defaultuser_ptr_id = %s;',
                                          [user_id])[0]
            form = AdvertiserEditForm(instance=user, readonly=True)

        return render(request, self.template_name, {'user': user,
                                                    'user_type': user_type,
                                                    'form': form,
                                                    'readonly': True})


class AccountView(View):
    template_name = "account.html"

    def get(self, request):
        if request.user.is_authenticated:
            cursor = connection.cursor()
            user_id = request.user.id
            # find the type of the user
            cursor.execute('select type '
                           'from auth_user '
                           'inner join accounts_defaultuser on id = user_ptr_id '
                           'where id = %s;', [user_id])
            user_type = cursor.fetchone()[0]
            cursor.close()

            form = None

            if user_type == 0:  # it is a Student account
                user = Student.objects.raw('select * from accounts_student where defaultuser_ptr_id = %s;',
                                           [user_id])[0]
                form = StudentEditForm(instance=user)

                cursor = connection.cursor()
                cursor.execute('select topic_id as topicname from main_interested_in '
                                           'where s_username_id = %s;', [user_id])
                interests = cursor.fetchall()
                cursor.close()
                interests_arr = []
                for interest in interests:
                    interests_arr.append(interest[0])
                print("-----------1-----------")
                print(interests_arr)

                cursor = connection.cursor()
                cursor.execute('select topicname from main_topic where topicname not in (select topic_id from main_interested_in '
                                           'where s_username_id = %s);', [user_id])
                not_in_interests = cursor.fetchall()
                not_interests_arr = []
                for not_interest in not_in_interests:
                    not_interests_arr.append(not_interest[0])

            elif user_type == 1:  # it is an Instructor account
                user = Instructor.objects.raw('select * from accounts_instructor where student_ptr_id = %s;',
                                              [user_id])[0]
                form = InstructorEditForm(instance=user)
            elif user_type == 2:  # advertiser account
                user = Advertiser.objects.raw('select * from accounts_advertiser where defaultuser_ptr_id = %s;',
                                              [user_id])[0]
                form = AdvertiserEditForm(instance=user)

            return render(request, self.template_name, {'user': user,
                                                        'user_type': user_type,
                                                        'form': form,
                                                        'readonly': False,
                                                        'interests': interests_arr,
                                                        'not_interests': not_interests_arr})
        return HttpResponseRedirect('/')  # redirects to main page if user did not login yet

    def post(self, request):
        cursor = connection.cursor()
        user_id = request.user.id
        # find the type of the user
        cursor.execute('select type '
                       'from auth_user '
                       'inner join accounts_defaultuser on id = user_ptr_id '
                       'where id = %s;', [user_id])
        user_type = cursor.fetchone()[0]
        cursor.close()
        cursor = connection.cursor()

        form = None

        if user_type == 0:  # it is a Student account
            user = Student.objects.raw('select * from accounts_student where defaultuser_ptr_id = %s;',
                                       [user_id])[0]
            form = StudentEditForm(request.POST, instance=user)
        elif user_type == 1:  # it is an Instructor account
            user = Instructor.objects.raw('select * from accounts_instructor where student_ptr_id = %s;',
                                          [user_id])[0]
            form = InstructorEditForm(request.POST, instance=user)
        elif user_type == 2:  # advertiser account
            user = Advertiser.objects.raw('select * from accounts_advertiser where defaultuser_ptr_id = %s;',
                                          [user_id])[0]
            form = AdvertiserEditForm(request.POST, instance=user)

        if form and form.is_valid():
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']  # every user has a phone field

            # update inside auth_user
            cursor.execute('update auth_user '
                           'set email = %s '
                           'where id = %s;',
                           [email, user_id])
            cursor.close()
            cursor = connection.cursor()

            if user_type == 0:  # student
                cursor.execute('update accounts_student '
                               'set phone = %s '
                               'where defaultuser_ptr_id = %s;',
                               [phone, user_id])
            elif user_type == 1:
                description = form.cleaned_data['description']
                cursor.execute('update accounts_instructor '
                               'set phone = %s, description = %s '
                               'where student_ptr_id = %s;',
                               [phone, description, user_id])
            elif user_type == 2:  # advertiser
                name = form.cleaned_data['name']
                company_name = form.cleaned_data['company_name']
                cursor.execute('update accounts_advertiser '
                               'set phone = %s, name = %s, company_name = %s '
                               'where defaultuser_ptr_id = %s;',
                               [phone, name, company_name, user_id])

        print(form.errors)
        cursor.close()
        return HttpResponseRedirect('/account')


class AdminView(View):
    def get(self, request):
        return HttpResponseRedirect('/')


def add_interested_topic(request, topic):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO main_interested_in(topic_id, s_username_id) values (%s, %s)",
                    [topic, request.user.id])
    cursor.close()
    return HttpResponseRedirect('/account')


def remove_interested_topic(request, topic):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM main_interested_in WHERE topic_id = %s AND s_username_id = %s",
                    [topic, request.user.id])
    cursor.close()
    return HttpResponseRedirect('/account')