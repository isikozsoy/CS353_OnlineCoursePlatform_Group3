import sys

from django.db import connection, DatabaseError, Error
from django.shortcuts import render, redirect
from django.views.generic.base import View, HttpResponseRedirect, HttpResponse
from django.contrib.auth import login, logout, authenticate

from .forms import *
from .models import Student, Instructor, SiteAdmin, Advertiser
from main.models import *
from main.views import MainView


class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect('/')


class LoginView(View):
    template_name = "login.html"

    def get(self, request, warning_message = None):
        if request.user.is_authenticated:
            return HttpResponseRedirect('/')

        form = Login()
        topic_list = Topic.objects.raw('select * from main_topic order by topicname;')
        print('select * from main_topic order by topicname;')
        return render(request, self.template_name, {'form': form,
                                                    'user_type': -1,
                                                    'topic_list': topic_list,
                                                    'warning_message': warning_message})

    def authenticate(self, request, username, password):
        user_q = User.objects.raw('select * from auth_user where username = %s and password = %s;',
                                  [username, password])
        print('select * from auth_user where username = ', username, ' and password = ', password, ';')
        return user_q

    def post(self, request):
        form = Login(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # checking if the user logs in as admin
            cursor = connection.cursor()
            cursor.execute('select is_superuser from auth_user where username = %s;', [username])
            print('select is_superuser from auth_user where username = ',username, ';')
            is_super = cursor.fetchone()
            cursor.close()
            if is_super and is_super[0] == 1:
                admin_set = self.authenticate(request, username=username, password=password)
                if admin_set:
                    login(request, admin_set[0])
                    return HttpResponseRedirect('/admin')
                return HttpResponseRedirect('/login')

            # continues if there is no admin by this username
            user_qset = self.authenticate(request, username=username, password=password)

            if user_qset:
                user = user_qset[0]
                login(request, user)
                return HttpResponseRedirect('/')
            else:  # no user by this username
                warning_message = "Either your username or your password is wrong."
                return LoginView.get(self, request, warning_message)



class RegisterView(View):
    template_name = "register.html"

    def get(self, request, warning_message = None):
        if request.user.is_authenticated:
            return HttpResponseRedirect('/')
        form = Register()

        cursor = connection.cursor()
        cursor.execute('select user_type '
                       'from auth_user '
                       'where id = %s;', [request.user.id])

        print('select user_type '
                       'from auth_user '
                       'where id = ',request.user.id,';')

        row = cursor.fetchone()
        user_type = -1
        if row:
            user_type = row[0]

        topic_list = Topic.objects.raw('select * from main_topic order by topicname;')
        print('select * from main_topic order by topicname;')

        return render(request, self.template_name, {'form': form,
                                                    'path': request.path,
                                                    'user_type': user_type,
                                                    'topic_list': topic_list,
                                                    'warning_message': warning_message})

    def exists(self, username):
        query = 'select * from auth_user where username = "' + username + '";'
        user_q = User.objects.raw(query)
        print(query)

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
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']

            # if the user already exists, return to the original registration page
            if self.exists(username):
                if "instructor" in request.path:

                    warning_message = "The username is taken"
                    return RegisterView.get(self, request, warning_message)

                elif "advertiser" in request.path:
                    warning_message = "The username is taken"
                    return RegisterView.get(self, request, warning_message)

                else:
                    warning_message = "The username is taken"
                    return RegisterView.get(self, request, warning_message)

            # we first create a new User object inside the auth.models.User model
            new_user = User(username=username, email=email, password=password)
            new_user.save()
            cursor = connection.cursor()
            cursor.execute('select id from auth_user where username = %s;', [username])
            print('select id from auth_user where username = ', username,';')
            user_id = cursor.fetchone()[0]

            cursor.execute('update auth_user set first_name = %s, last_name = %s where id = %s;',
                           [first_name, last_name, user_id])
            print('update auth_user set first_name = ', first_name, ', last_name = ',last_name,' where id = ', user_id, ';')

            # Then we go on to add this model to the corresponding submodels, i.e. DefaultUser where password_orig
            #  will be saved, Student, Instructor, Advertiser, etc. For this, we need the id of the user that we added
            #  previously.

            # The registration type is determined from the path the user takes for the account
            if "advertiser" in request.path:
                company_name = form.cleaned_data['company_name']

                cursor.close()
                cursor = connection.cursor()
                cursor.execute(
                    "insert into accounts_advertiser(user_ptr_id, name, company_name, phone) "
                    "values ( %s, %s, %s, %s)",
                    [user_id, "", company_name, phone])
                print("insert into accounts_advertiser(user_ptr_id, name, company_name, phone) "
                    "values ( ", user_id, ",  , ", company_name, ", ", phone, ")")
            elif "instructor" in request.path:
                description = form.cleaned_data['description']

                cursor.close()
                cursor = connection.cursor()
                cursor.execute(
                    "insert into accounts_student(user_ptr_id, phone) values ( %s, %s)",
                    [user_id, phone])
                print('insert into accounts_student(user_ptr_id, phone) values ( ',user_id, ', ', phone, ')')
                cursor.close()
                cursor = connection.cursor()
                cursor.execute(
                    "insert into accounts_instructor(student_ptr_id, description) values ( %s, %s)",
                    [new_user.id, description])
                print('insert into accounts_instructor(student_ptr_id, description) values ( ', new_user.id, ', ', description, ')')
            else:
                cursor.close()
                cursor = connection.cursor()
                cursor.execute(
                    "insert into accounts_student(user_ptr_id, phone) values ( %s, %s)",
                    [user_id, phone])
                print('insert into accounts_student(user_ptr_id, phone) values ( ', user_id, ', ', phone, ')')

            cursor.close()
            return HttpResponseRedirect('/login')  # /login
        warning_message = "The form values were not valid."
        return RegisterView.get(self, request, warning_message)


class UserView(View):
    template_name = "account.html"

    def get(self, request, username):
        cursor = connection.cursor()
        cursor.execute('select id from auth_user where username = %s;', [username])
        print('select id from auth_user where username = ',username,';')
        user_id_row = cursor.fetchone()
        cursor.close()

        if not user_id_row:  # this means that the user with the username does not exist
            warning_message = "Error: There is no user by this username."
            return MainView.get(self, request, warning_message)

        user_id = user_id_row[0]

        if request.user.is_authenticated and request.user.id == user_id:
            return HttpResponseRedirect('/account')

        # now we need to get the user type
        cursor = connection.cursor()

        # find the type of the user
        cursor.execute('select user_type '
                       'from auth_user '
                       'where id = %s;', [user_id])
        user_type = cursor.fetchone()[0]
        print('select user_type '
                       'from auth_user '
                       'where id = ', user_id, ';')
        cursor.close()

        if user_type == 0:  # it is a Student account
            user = Student.objects.raw('select * from accounts_student where user_ptr_id = %s;',
                                       [user_id])[0]
        elif user_type == 1:  # it is an Instructor account
            user = Instructor.objects.raw('select * from accounts_instructor where student_ptr_id = %s;',
                                          [user_id])[0]
        elif user_type == 2:  # advertiser account
            user = Advertiser.objects.raw('select * from accounts_advertiser where user_ptr_id = %s;',
                                          [user_id])[0]
        else:
            user = SiteAdmin.objects.raw('select * from accounts_advertiser where user_ptr_id = %s;',
                                          [user_id])[0]
        form = AccountViewForm(user_type=user_type, user=user, readonly=True)

        topic_list = Topic.objects.raw('select * from main_topic order by topicname;')

        return render(request, self.template_name, {'user': user,
                                                    'user_type': user_type,
                                                    'form': form,
                                                    'readonly': True,
                                                    'topic_list': topic_list, })


class AccountView(View):
    template_name = "account.html"

    def get(self, request):
        if request.user.is_authenticated:
            cursor = connection.cursor()
            try:
                cursor.execute('select user_type '
                               'from auth_user '
                               'where id = %s;', [request.user.id])
                user_type = cursor.fetchone()
                print('select user_type '
                               'from auth_user '
                               'where id = ', request.user.id, ';')
                if user_type:
                    user_type = user_type[0]
            except Error:
                return HttpResponse('There was an error. <p> Check the error message below: <p>' + sys.exc_info())
            finally:
                cursor.close()

            if user_type == 0:  # it is a Student account
                user = Student.objects.raw('select * from accounts_student where user_ptr_id = %s;',
                                           [request.user.id])[0]

            elif user_type == 1:  # it is an Instructor account
                user = Instructor.objects.raw('select * from accounts_instructor where student_ptr_id = %s;',
                                              [request.user.id])[0]

            elif user_type == 2:  # advertiser account
                user = Advertiser.objects.raw('select * from accounts_advertiser where user_ptr_id = %s;',
                                              [request.user.id])[0]
            else:  # admin
                user = SiteAdmin.objects.raw('select * from accounts_siteadmin where user_ptr_id = %s;',
                                             [request.user.id])[0]

            form = AccountViewForm(user_type=user_type, user=user, readonly=False)

            cursor = connection.cursor()
            try:
                cursor.execute('select topic_id as topicname from main_interested_in '
                               'where s_username_id = %s;', [request.user.id])
                interests = cursor.fetchall()
                print('select topic_id as topicname from main_interested_in '
                               'where s_username_id = ', request.user.id, ';')
                interests_arr = []
                for interest in interests:
                    interests_arr.append(interest[0])
            except Error:
                return HttpResponse('There was an error. <p> Check the error message below: <p>' + sys.exc_info())
            finally:
                cursor.close()

            cursor = connection.cursor()
            try:
                cursor.execute(
                    'select topicname from main_topic where topicname not in (select topic_id from main_interested_in '
                    'where s_username_id = %s);', [request.user.id])
                print('select topicname from main_topic where topicname not in (select topic_id from main_interested_in '
                    'where s_username_id = ', request.user.id, ');')

                not_in_interests = cursor.fetchall()
                not_interests_arr = []
                for not_interest in not_in_interests:
                    not_interests_arr.append(not_interest[0])
            except Error:
                return HttpResponse('There was an error. <p> Check the error message below: <p>' + sys.exc_info())
            finally:
                cursor.close()

            topic_list = Topic.objects.raw('select * from main_topic order by topicname;')

            return render(request, self.template_name, {'user': user,
                                                        'user_type': user_type,
                                                        'form': form,
                                                        'readonly': False,
                                                        'topic_list': topic_list,
                                                        'interests': interests_arr,
                                                        'not_interests': not_interests_arr, })
        return HttpResponseRedirect('/login')

    def post(self, request):
        cursor = connection.cursor()
        try:
            user_id = request.user.id
            # find the type of the user
            cursor.execute('select user_type '
                           'from auth_user '
                           'where id = %s;', [user_id])
            print('select user_type '
                           'from auth_user '
                           'where id = ', user_id, ';')
            user_type = cursor.fetchone()
            if user_type:
                user_type = user_type[0]
        except Error:
            return HttpResponse('There was an error. <p> Check the error message below: <p>' + sys.exc_info())
        finally:
            cursor.close()

        if user_type == 0:  # it is a Student account
            user = Student.objects.raw('select * from accounts_student where user_ptr_id = %s;',
                                       [request.user.id])[0]
        elif user_type == 1:  # it is an Instructor account
            user = Instructor.objects.raw('select * from accounts_instructor where student_ptr_id = %s;',
                                          [request.user.id])[0]
        elif user_type == 2:  # advertiser account
            user = Advertiser.objects.raw('select * from accounts_advertiser where user_ptr_id = %s;',
                                          [request.user.id])[0]
        else:  # admin
            user = SiteAdmin.objects.raw('select * from accounts_siteadmin where user_ptr_id = %s;',
                                         [request.user.id])[0]

        form = AccountViewForm(request.POST, user_type=user_type, user=user, readonly=False)
        if form.is_valid():
            email = form.cleaned_data['email']
            if user_type != 3:
                phone = form.cleaned_data['phone']

            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']

            if first_name:
                cursor = connection.cursor()
                try:
                    cursor.execute('update auth_user '
                                   'set first_name = %s '
                                   'where id = %s;',
                                   [first_name, user_id])

                    print('update auth_user '
                                   'set first_name = ', first_name,' '
                                   'where id = ', user_id, ';')
                finally:
                    cursor.close()

            if last_name:
                cursor = connection.cursor()
                try:
                    cursor.execute('update auth_user '
                                   'set last_name = %s '
                                   'where id = %s;',
                                   [last_name, user_id])

                    print('update auth_user '
                                   'set last_name = ', last_name, ' '
                                   'where id = ', user_id,';')
                finally:
                    cursor.close()

            if email:
                cursor = connection.cursor()
                try:
                    cursor.execute('update auth_user '
                                   'set email = %s '
                                   'where id = %s;',
                                   [email, user_id])
                    print('update auth_user '
                                   'set email = ', email, ' '
                                   'where id = ', user_id, ';')
                finally:
                    cursor.close()

            if user_type == 0:  # student
                if phone:
                    cursor = connection.cursor()
                    try:
                        cursor.execute('update accounts_student '
                                       'set phone = %s '
                                       'where user_ptr_id = %s;',
                                       [phone, user_id])
                        print('update accounts_student '
                                       'set phone = ',phone , ' '
                                       'where user_ptr_id = ', user_id, ';')

                    finally:
                        cursor.close()
            elif user_type == 1: # instructor, so phone and description need to be updated
                description = form.cleaned_data['description']
                if description:
                    cursor = connection.cursor()
                    try:
                        cursor.execute('update accounts_instructor '
                                       'set description = %s '
                                       'where student_ptr_id = %s;',
                                       [description, user_id])
                        print('update accounts_instructor '
                                       'set description = ', description,' '
                                       'where student_ptr_id = ', user_id, ';')
                    finally:
                        cursor.close()
                if phone:
                    cursor = connection.cursor()
                    try:
                        cursor.execute('update accounts_student '
                                       'set phone = %s '
                                       'where user_ptr_id = %s;',
                                       [phone, user_id])
                        print('update accounts_student '
                                       'set phone = ', phone, ' '
                                       'where user_ptr_id = ', user_id, ';')
                    finally:
                        cursor.close()
            elif user_type == 2:  # advertiser, so phone, company_name and name need to be updated
                company_name = form.cleaned_data['company_name']
                name = form.cleaned_data['name']
                if phone:
                    cursor = connection.cursor()
                    try:
                        cursor.execute('update accounts_advertiser '
                                       'set phone = %s '
                                       'where user_ptr_id = %s;',
                                       [phone, user_id])
                        print('update accounts_advertiser '
                                       'set phone = ', phone, ' '
                                       'where user_ptr_id = ', user_id, ';')
                    finally:
                        cursor.close()
                if company_name:
                    cursor = connection.cursor()
                    try:
                        cursor.execute('update accounts_advertiser '
                                       'set company_name = %s '
                                       'where user_ptr_id = %s;',
                                       [company_name, user_id])
                        print('update accounts_advertiser '
                                       'set company_name = ', company_name, ' '
                                       'where user_ptr_id = ', user_id, ';')
                    finally:
                        cursor.close()
                if name:
                    cursor = connection.cursor()
                    try:
                        cursor.execute('update accounts_advertiser '
                                       'set name = %s '
                                       'where user_ptr_id = %s;',
                                       [name, user_id])
                        print('update accounts_advertiser '
                                       'set name = ', name,' '
                                       'where user_ptr_id = ', user_id, ';')
                    finally:
                        cursor.close()
            #else:  # admin
        else:
            print(form.errors)
            return HttpResponse('Your form values were not valid. <a href="/account">Return to your account page...</a>')

        return redirect('accounts:account')


def add_interested_topic(request, topic):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO main_interested_in(topic_id, s_username_id) values (%s, %s)",
                   [topic, request.user.id])
    print("INSERT INTO main_interested_in(topic_id, s_username_id) values (", topic, ", ", request.user.id,")")
    cursor.close()
    return HttpResponseRedirect('/account')


def remove_interested_topic(request, topic):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM main_interested_in WHERE topic_id = %s AND s_username_id = %s",
                   [topic, request.user.id])

    print("DELETE FROM main_interested_in WHERE topic_id = ", topic, " AND s_username_id = ", request.user.id)
    cursor.close()
    return HttpResponseRedirect('/account')

def update_to_instructor(request):
    cursor = connection.cursor()
    cursor.execute('INSERT INTO accounts_instructor(student_ptr_id, description) values (%s, %s)',
                   [request.user.id, ""])
    print('INSERT INTO accounts_instructor(student_ptr_id, description) values (', request.user.id, ',  )')
    cursor.execute('UPDATE auth_user SET user_type = 1 WHERE id = %s', request.user.id)
    print('UPDATE auth_user SET user_type = 1 WHERE id = ', request.user.id)
    return HttpResponseRedirect('/account')
