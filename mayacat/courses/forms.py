from django import forms
from django.db import connection

from .models import Course
from main.models import Course_Topic, Topic
from datetime import datetime, date, timedelta
from main.models import Post

class AddTeacherForm(forms.Form):
    addteacher = forms.CharField(label='addteacher', max_length=500)

class AddContributorForm(forms.Form):
    addcontributor = forms.CharField(label='addcontributor', max_length=500)

class AddAnnouncementForm(forms.Form):
    addannouncement = forms.CharField(label='addannouncement', max_length=500)

class TeacherDelete(forms.Form):
    addteacher = forms.CharField(label='addteacher', max_length=500)

class NewNoteForm(forms.Form):
    note = forms.CharField(label='note', max_length=500)
class AskQuestion(forms.Form):
    question = forms.CharField(label='question', max_length=500)

class AnswerQuestion(forms.Form):
    question_no=-1
    print("In form question_no: ",question_no)
    answer = forms.CharField(label='answer' + str(question_no), max_length=500)

class FinishCourseCommentForm(forms.Form):
    comment = forms.CharField(label='comment', max_length = 1000)

CHOICES = [('one','one'),('two','two'),('three','three'),('four','four'),('five','five')]
class FinishCourseRateForm(forms.Form):
    rate = forms.ChoiceField(widget=forms.RadioSelect,choices=CHOICES)

class ComplainForm(forms.Form):
    description = forms.CharField(label='Description', max_length=1000)

class GiftInfo(forms.Form):
    is_gift = forms.BooleanField(label='Add to cart as a gift: ', required=False)

class AddAsGift(forms.Form):
    course_slug = forms.CharField(label='Course Slug', max_length = 50)

class FirstLastName(forms.Form):
    first_name = forms.CharField(label='First Name', max_length=150)
    last_name = forms.CharField(label='Last Name', max_length=150)


class CreateCourseForm(forms.Form):
    course_img = forms.CharField(label='Embedded Image URL for Course', max_length=100,
                                  widget=forms.TextInput(attrs={'class': 'form-control'}))
    cname = forms.CharField(label='Course name:', max_length=50,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'A Course Name'}))
    price = forms.DecimalField(label='Price (up to $9999.99)', max_digits=6, decimal_places=2,
                               widget=forms.NumberInput(attrs={'class': 'form-control'}))

    cursor = connection.cursor()
    cursor.execute('select topicname from main_topic;')

    topic = forms.ModelMultipleChoiceField(Topic.objects.filter(topicname__in=(x[0] for x in cursor)),
                                           label='Topic', widget=forms.CheckboxSelectMultiple(
        attrs={'class': 'select'}))

    description = forms.CharField(label='Description', max_length=4000,
                                  widget=forms.Textarea(attrs={'class': 'form-control'}))
    private = forms.BooleanField(label='Private', required=False)


class EditCourseForm(forms.ModelForm):
    course_img = forms.CharField(label='Embedded Image URL for Course', max_length=100,
                                  widget=forms.TextInput(attrs={'class': 'form-control'}))

    cname = forms.CharField(label='Course name:', max_length=50,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'A Course Name'}))
    price = forms.DecimalField(label='Price (up to $9999.99)', max_digits=6, decimal_places=2,
                               widget=forms.NumberInput(attrs={'class': 'form-control'}))
    description = forms.CharField(label='Description', max_length=4000,
                                  widget=forms.Textarea(attrs={'class': 'form-control'}))
    private = forms.BooleanField(label='Private', required=False)

    class Meta:
        model = Course
        fields = ('course_img', 'cname', 'price', 'description', 'is_private')


class EditTopicForm(forms.ModelForm):
    cursor = connection.cursor()
    cursor.execute('select topicname from main_topic;')

    topic = forms.ModelMultipleChoiceField(Topic.objects.filter(topicname__in=(x[0] for x in cursor)),
                                           label='Topic', widget=forms.CheckboxSelectMultiple(
        attrs={'class': "select"}))

    class Meta:
        model = Course_Topic
        fields = ('topicname',)


class OfferAdForm(forms.Form):
    ad_img = forms.CharField(label='Embedded Image URL for Advertisement', max_length=100,
                                  widget=forms.TextInput(attrs={'class': 'form-control'}))
    price = forms.DecimalField(label='Offered Price (TL)', max_digits=6, decimal_places=2,
                               widget=forms.NumberInput(attrs={'class': 'form-control'}))
    start_date = forms.DateField(label='Start Date', initial=date.today, widget=forms.DateInput(
        attrs={'class': 'form-control datepicker-input', 'type': 'date'})
)
    end_date = forms.CharField(label='End Date', initial=date.today, widget=forms.DateInput(
        attrs={'class': 'form-control datepicker-input', 'type': 'date'}))


class CreateLectureForm(forms.Form):
    lecture_url = forms.CharField(label='Embedded URL for Lecture', max_length=100,
                                  widget=forms.TextInput(attrs={'class': 'form-control'}))
    lecture_name = forms.CharField(label='Lecture Name', max_length=50,
                                   widget=forms.TextInput(attrs={'class': 'form-control',
                                                                 'placeholder': 'A Lecture Name'}))


class CreateAssignmentAndLectureMaterialForm(forms.Form):
    pdf_url_assignment = forms.CharField(label='PDF Link from Google Drive for Assignment', max_length=100,
                                         widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    pdf_url_lecmat = forms.CharField(label='PDF Link from Google Drive for Lecture Material', max_length=100,
                                     widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
