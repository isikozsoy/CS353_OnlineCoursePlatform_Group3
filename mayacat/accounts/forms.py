from django import forms


class Login(forms.Form):
    username = forms.CharField(label='Username', max_length=50)
    password = forms.CharField(label='Password', max_length=50)


class Register(forms.Form):
    username = forms.CharField(label='Username', max_length=50)
    email = forms.CharField(label='Email', max_length=50)
    phone = forms.CharField(label='Phone', max_length=50)
    password = forms.CharField(label='Password', max_length=50)

class InstructorProfile(forms.Form):
    username = forms.CharField(label='Username', max_length=50)
    email = forms.CharField(label='Email', max_length=50)
    phone = forms.CharField(label='Phone', max_length=50)
    password = forms.CharField(label='Password', max_length=50)
    description = forms.CharField(label='Description', max_length=1000)


"""
class NewLectureForm(forms.Form):
    lecture_name = forms.CharField(label='Title', max_length=200)
    video_file = forms.FileField()
"""
