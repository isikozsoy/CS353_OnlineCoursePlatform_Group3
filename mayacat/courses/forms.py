from django import forms
from .models import Course


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
    course_img = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control-file',
                                                                'enctype': 'multipart/form-data'}))
    cname = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control',
                                                                         'placeholder': 'A Course Name'}))
    price = forms.DecimalField(max_digits=6, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    topic = forms.ChoiceField(label='Topic', choices=TOPIC_CHOICES, widget=forms.Select(
        attrs={'class': "form-control"}))

    description = forms.CharField(max_length=4000, widget=forms.Textarea(attrs={'class': 'form-control'}))
    private = forms.BooleanField(label='Private?', required=False)

