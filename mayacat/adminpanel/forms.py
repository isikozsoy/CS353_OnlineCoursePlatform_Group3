from django import forms
from django.db import connection

from accounts.models import Instructor
from main.models import Topic
from courses.models import Lecture
from .models import Offered_Discount


class SiteAdminSaveForm(forms.Form):
    ssn = forms.CharField(label='Social Security Number', max_length=20, widget=forms.TextInput)
    address = forms.CharField(label='Address', max_length=100, widget=forms.TextInput)


class InstructorCreate(forms.Form):
    description = forms.CharField(label='Description', max_length=1000)


class AdvertiserCreate(forms.Form):
    name = forms.CharField(label='Name & Surname', max_length=50)
    company_name = forms.CharField(label='Company Name', max_length=50)


class UserCreate(forms.Form):
    username = forms.CharField(label='Username', max_length=50)
    email = forms.CharField(label='Email', max_length=50)
    phone = forms.CharField(label='Phone', max_length=50)
    password = forms.CharField(label='Password', max_length=50)


class SiteAdminCreate(forms.Form):
    ssn = forms.CharField(label='Social Security Number', max_length=20)
    address = forms.CharField(label='Address', max_length=100)


class CourseCreate(forms.Form):
    cursor = connection.cursor()

    try:
        cursor.execute('select student_ptr_id from accounts_instructor')
        owner = forms.ModelChoiceField(Instructor.objects.filter(student_ptr_id__in=(x[0] for x in cursor)),
                                       label='Owner',
                                       widget=forms.Select(attrs={'class': "form-control"}))
        cursor.execute('select topicname from main_topic')
        topic = forms.ModelMultipleChoiceField(Topic.objects.filter(topicname__in=(x[0] for x in cursor)),
                                               label='Topic',
                                               widget=forms.CheckboxSelectMultiple(attrs={'class': "select"}))
    finally:
        cursor.close()

    course_img = forms.ImageField(label='Thumbnail', widget=forms.FileInput(attrs={'class': 'form-control-file',
                                                                                   'enctype': 'multipart/form-data'}))
    cname = forms.CharField(label='Course name', max_length=50,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'A Course Name'}))
    price = forms.DecimalField(label='Price (up to $9999.99)', max_digits=6, decimal_places=2,
                               widget=forms.NumberInput(attrs={'class': 'form-control'}))
    description = forms.CharField(label='Description', max_length=4000,
                                  widget=forms.Textarea(attrs={'class': 'form-control'}))
    private = forms.BooleanField(label='Private or not?', required=False)


class LectureCreate(forms.Form):
    cursor = connection.cursor()

    try:
        cursor.execute('select cno from courses_course')
        course = forms.ModelChoiceField(Lecture.objects.filter(cno_id__in=(x[0] for x in cursor)), label='Topic',
                                        widget=forms.Select(attrs={'class': "form-control"}))
    finally:
        cursor.close()

    lecture_name = forms.CharField(label='Course name', max_length=50,
                                   widget=forms.TextInput(
                                       attrs={'class': 'form-control', 'placeholder': 'A Course Name'}))
    video_url = forms.CharField(label='Video URL', max_length=200, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'yt.be/embed/some_embedded_code'}))


class DiscountForm(forms.Form):
    percentage = forms.IntegerField(label='Percentage', widget=forms.NumberInput(attrs={'class': 'form-control', }))
    start_date = forms.DateField(label='Start Date',
                                 input_formats=['%Y-%m-%d'],
                                 widget=forms.DateInput(attrs={'class': 'datepicker-input',
                                                               'type': 'date'
                                                               }))
    end_date = forms.DateField(label='End Date',
                               input_formats=['%Y-%m-%d'],
                               widget=forms.DateInput(attrs={'class': 'form-control datepicker-input',
                                                             'type': 'date'
                                                             }))
