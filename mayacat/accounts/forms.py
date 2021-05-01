from django import forms
from .models import Student


class EditForm(forms.ModelForm):
    email = forms.CharField(label='Email', max_length=50, widget=forms.TextInput())
    phone = forms.CharField(label='Phone', max_length=50, widget=forms.TextInput())
    description = forms.CharField(label='Description', max_length=50, required=False, widget=forms.TextInput())

    class Meta:
        model = Student
        fields = ('email', 'phone', 'description')


class Login(forms.Form):
    username = forms.CharField(label='Username', max_length=50)
    password = forms.CharField(label='Password', max_length=50, widget=forms.PasswordInput)


class Register(forms.Form):
    username = forms.CharField(label='Username', max_length=50)
    email = forms.CharField(label='Email', max_length=50)
    phone = forms.CharField(label='Phone', max_length=50)

    description = forms.CharField(label='Description', max_length=1000, required=False)

    name = forms.CharField(label='Name & Surname', max_length=50, required=False)
    company_name = forms.CharField(label='Company Name', max_length=50, required=False)

    password = forms.CharField(label='Password', max_length=50, widget=forms.PasswordInput)


"""
class NewLectureForm(forms.Form):
    lecture_name = forms.CharField(label='Title', max_length=200)
    video_file = forms.FileField()
"""