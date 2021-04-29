from django.db import connections
from django.shortcuts import render, redirect
from django.views.generic.base import View, HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, logout

from .forms import *
from .models import DefaultUser, Student, Instructor, SiteAdmin, Advertiser

cursor = connections['default'].cursor()


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
        return render(request, self.template_name, {'form': form,
                                                    'path': request.path})

    def exists(self, username):
        query = 'select * from auth_user where username = "' + username + '";'
        user_q = User.objects.raw(query)

        if user_q:
            return True
        return False

    def post(self, request):
        form = Register(request.POST)
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
                cursor.execute(
                    "insert into accounts_advertiser(defaultuser_ptr_id, name, company_name) values ( %s, %s, %s)",
                    [new_user.id, name, company_name])
            elif "instructor" in request.path:
                description = form.cleaned_data['description']

                cursor.execute(
                    "insert into accounts_defaultuser(user_ptr_id, password_orig, type) values ( %s, %s, %s)",
                    [new_user.id, password, 1])
                cursor.execute(
                    "insert into accounts_student(defaultuser_ptr_id, phone, description) values ( %s, %s, %s)",
                    [new_user.id, phone, description])
                cursor.execute(
                    "insert into accounts_instructor(student_ptr_id) values ( %s)",
                    new_user.id)
            else:
                cursor.execute(
                    "insert into accounts_defaultuser(user_ptr_id, password_orig, type) values ( %s, %s, %s)",
                    [new_user.id, password, 0])
                cursor.execute(
                    "insert into accounts_student(defaultuser_ptr_id, phone, description) values ( %s, %s, %s)",
                    [new_user.id, phone, ""])

            new_user.save()
            return HttpResponseRedirect('/login')  # /login
        else:
            print("Wrong form values")
        return HttpResponse('This is Register view.')
