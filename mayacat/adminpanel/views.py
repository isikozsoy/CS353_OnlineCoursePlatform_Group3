from django.contrib.auth.models import User
from django.db import connection
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

# Create your views here.
from django.views.generic import View

from .forms import *


class AdminFirstRegisterView(View):
    template_name = "adminpanel/register.html"

    def get(self, request):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return HttpResponseRedirect('/')
        # also check if the user needs to refresh their ssn and address

        # ask for ssn and address
        admin_save_form = SiteAdminSaveForm()
        return render(request, self.template_name, {'admin_save_form': admin_save_form})

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


class AdminView(View):  # this page is '/admin'
    template_name = "adminpanel/admin_main.html"

    def get(self, request):
        # first all the evaluations to be done are listed
        if not request.user.is_superuser:
            return HttpResponseRedirect('/')

        self.save_as_siteadmin(request.user.id)

        form_user = UserCreate()
        form_instructor = InstructorCreate()
        form_advertiser = AdvertiserCreate()
        form_siteadmin = SiteAdminCreate()

        return render(request, self.template_name, {'form_user': form_user,
                                                    'form_instructor': form_instructor,
                                                    'form_advertiser': form_advertiser,
                                                    'form_siteadmin': form_siteadmin, })

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
                return HttpResponseRedirect('/admin')

        cursor.close()

        return redirect('adminpanel:admin_main')

    def save_as_siteadmin(self, user_id):
        cursor = connection.cursor()
        cursor.execute('select user_ptr_id from accounts_defaultuser where user_ptr_id = %s;', [user_id])
        selected = cursor.fetchall()
        cursor.close()
        if not selected:  # if the user is not officially saved
            return HttpResponseRedirect('/admin/register')
