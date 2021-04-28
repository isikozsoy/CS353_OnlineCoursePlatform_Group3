from django.shortcuts import render, redirect
from django.views.generic.base import View, HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, logout

from .forms import *
from .models import DefaultUser, Student, Instructor, SiteAdmin, Advertiser


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
            #new_user = User(username=username, email=email)
            #new_user.set_password(password)
            #new_user.save()

            # then we go on to add this model to the corresponding submodels, i.e. DefaultUser where password_orig
            #  will be saved, Student, Instructor, Advertiser, etc. For this, we need the id of the user that we added
            #  previously.
            #user = User.objects.raw('select id from auth_user where username = "' + username + '";')[0]
            #user_id = user.id

            # The registration type is determined from the path the user takes for the account
            if "advertiser" in request.path:
                name = form.cleaned_data['name']; company_name = form.cleaned_data['company_name']
                new_user = Advertiser(username=username, email=email, password_orig=password, type=2, name=name,
                                      company_name=company_name, password=password)
                #DefaultUser.objects.raw('insert into accounts_defaultuser (user_ptr_id, password_orig, type) '
                 #                       'values ("' + user_id + '", "' + password + '", 2);')
                #Advertiser.objects.raw('insert into accounts_advertiser (defaultuser_ptr_id, name, company_name) '
                 #                      'values ("' + user_id + '", "' + name + '", "' + company_name + '");')

            elif "instructor" in request.path:
                description = form.cleaned_data['description']
                new_user = Instructor(username=username, email=email, phone=phone, password_orig=password, type=1,
                                      description=description, password=password)
                #DefaultUser.objects.raw('insert into accounts_defaultuser (user_ptr_id, password_orig, type) '
                 #                       'values ("' + user_id + '", "' + password + '", 1);')
                #Instructor.objects.raw('insert into accounts_student (defaultuser_ptr_id, description) ' \
                 #                      'values ("' + user_id + '", "' + description + '");')
            else:
                new_user = Student(username=username, email=email, phone=phone, password_orig=password, type=0,
                                   password=password)
                #DefaultUser.objects.raw('insert into accounts_defaultuser (user_ptr_id, password_orig, type) '
                                        #'values (' + str(user_id) + ', "' + password + '", 0);')[0].save()
                #new_user = Student.objects.raw('insert into accounts_student (username, email, phone, password_orig, type) ' \
                 #                   'values ("' + username + '", "' + email + '", "' + phone + '", "' + password + '", 0);')[0]

            new_user.save()
            #            new_user.username = username; new_user.email = email
            #            new_user.phone = phone; new_user.password_orig = password

            return HttpResponseRedirect('/login')  # /login
        else:
            print("Wrong form values")
        return HttpResponse('This is Register view.')
