from django import forms
from .models import Course
from main.models import Post

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
class FinishCourseRateForm(forms.Form):
    rate = forms.CharField(label='rate', max_length = 1000)


class ComplainForm(forms.Form):
    description = forms.CharField(label='Description', max_length=1000)

class GiftInfo(forms.Form):
    username = forms.CharField(label='Username', max_length=50)


TOPIC_CHOICES = (
    ("Design", "Design"),
    ("Development", "Development"),
    ("Marketing", "Marketing"),
    ("IT and Software", "IT and Software"),
    ("Personal Development", "Personal Development"),
    ("Business", "Business"),
    ("Music", "Music"),
    ("Other", "Other"),
)


class CreateCourseForm(forms.Form):
    course_img = forms.ImageField(label='Thumbnail', widget=forms.FileInput(attrs={'class': 'form-control-file',
                                                                                   'enctype': 'multipart/form-data'}))
    cname = forms.CharField(label='Course name:', max_length=50,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'A Course Name'}))
    price = forms.DecimalField(label='Price (up to $9999.99)', max_digits=6, decimal_places=2,
                               widget=forms.NumberInput(attrs={'class': 'form-control'}))
    topic = forms.ChoiceField(label='Topic', choices=TOPIC_CHOICES, widget=forms.Select(
        attrs={'class': "form-control"}))

    description = forms.CharField(label='Description', max_length=4000,
                                  widget=forms.Textarea(attrs={'class': 'form-control'}))
    private = forms.BooleanField(label='Private or not?', required=False)


class CreateLectureForm(forms.Form):
    lecture_url = forms.CharField(label='Embedded URL for Lecture', max_length=100,
                                  widget=forms.TextInput(attrs={'class': 'form-control'}))
    lecture_name = forms.CharField(label='Lecture Name', max_length=50,
                                   widget=forms.TextInput(attrs={'class': 'form-control',
                                                                 'placeholder': 'A Lecture Name'}))


class CreateAssignmentAndLectureMaterialForm(forms.Form):
    pdf_url_assignment = forms.CharField(label='PDF Link from Google Drive', max_length=100,
                                         widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    pdf_url_lecmat = forms.CharField(label='PDF Link from Google Drive', max_length=100,
                                     widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
