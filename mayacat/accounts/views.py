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
        return render(request, self.template_name, {'form':form})

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

class RegisterInstructorView(View):
    template_name = "register_instructor.html"

    def get(self, request):
        if request.user.is_authenticated:
            return HttpResponseRedirect('/')
        form = InstructorProfile()
        return render(request, self.template_name, {'form':form})

    def post(self, request):
        form = InstructorProfile(request.POST)
        if form.is_valid():
            # new user account that is automatically a Student as well
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            description = form.cleaned_data['description']

            new_user = Instructor(username=username, email=email, phone=phone, description=description)
            new_user.set_password(password)
            new_user.save()

            return HttpResponseRedirect('/') # go to the instructor page
        return HttpResponse('This is Register view.')

class RegisterView(View):
    template_name = "register.html"

    def get(self, request):
        if request.user.is_authenticated:
            print('Already logged in. Redirecting to the main page...')
            print(request.user)
            return HttpResponseRedirect('/')
        form = Register()
        return render(request, self.template_name, {'form':form})

    def post(self, request):
        form = Register(request.POST)
        if form.is_valid():
            # new user account that is automatically a Student as well
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']

            new_user = Student(username=username, email=email, phone=phone)
            new_user.set_password(password)
            new_user.save()

            return HttpResponseRedirect('/') #/login
        else:
            print("Wrong form values")
        return HttpResponse('This is Register view.')