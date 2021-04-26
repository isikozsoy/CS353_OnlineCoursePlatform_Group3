from django.shortcuts import render
from django.views.generic.base import View, HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from .forms import *
from main.models import Student, Instructor, SiteAdmin


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

    def post(self, request):
        form = Login(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                print('Wrong username or password. Redirecting...')
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

    def post(self, request):
        form = Register(request.POST)
        if form.is_valid():
            # new user account that is automatically a Student as well
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']

            if "advertiser" in request.path:
                new_user = Advertiser()
                new_user.type = 2
            elif "instructor" in request.path:
                new_user = Instructor()
                new_user.type = 1
            else:
                new_user = Student()
                new_user.type = 0

            new_user.username = username; new_user.email = email; new_user.phone = phone
            new_user.set_password(password)
            new_user.save()

            return HttpResponseRedirect('/')  # /login
        else:
            print("Wrong form values")
        return HttpResponse('This is Register view.')
