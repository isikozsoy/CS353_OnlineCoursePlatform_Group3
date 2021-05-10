from django.db import connection
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.views.generic import View

from .forms import SiteAdminSaveForm


class AdminFirstRegisterView(View):
    def get(self, request):
        # ask for ssn and address
        admin_save_form = SiteAdminSaveForm()


class AdminView(View):  # this page is '/admin'
    def get(self, request):
        # first all the evaluations to be done are listed
        user_id = request.user.id

        cursor = connection.cursor()

        self.save_as_siteadmin()

        cursor.close()
        return HttpResponseRedirect('/')

    def save_as_siteadmin(self, user_id):
        cursor = connection.cursor()
        cursor.execute('select user_ptr_id from accounts_defaultuser where user_ptr_id = %s;', [user_id])
        selected = cursor.fetchall()
        if not selected: # if the user is not officially saved
            return HttpResponseRedirect('/admin/register')