from django import forms
from .models import *


class StudentEditForm(forms.ModelForm):
    email = forms.CharField(label='Email', max_length=50,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}))
    phone = forms.CharField(label='Phone', max_length=50,
                            widget=forms.TextInput(attrs={'class': 'form-control'}))

    def __init__(self, readonly=False, *args, **kwargs):
        super(StudentEditForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['email'].widget.attrs['readonly'] = readonly
            self.fields['phone'].widget.attrs['readonly'] = readonly

    class Meta:
        model = Student
        fields = ('email', 'phone')


class InstructorEditForm(forms.ModelForm):
    email = forms.CharField(label='Email', max_length=50,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}))
    phone = forms.CharField(label='Phone', max_length=50,
                            widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(label='Description', max_length=50, required=False,
                                  widget=forms.TextInput(attrs={'class': 'form-control',
                                                                'placeholder': 'A description'}))

    def __init__(self, readonly=False, *args, **kwargs):
        super(InstructorEditForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['email'].widget.attrs['readonly'] = readonly
            self.fields['phone'].widget.attrs['readonly'] = readonly
            self.fields['description'].widget.attrs['readonly'] = readonly

    class Meta:
        model = Instructor
        fields = ('email', 'phone', 'description')


class AdvertiserEditForm(forms.ModelForm):
    email = forms.CharField(label='Email', max_length=50,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}))
    phone = forms.CharField(label='Phone', max_length=50,
                            widget=forms.TextInput(attrs={'class': 'form-control'}))
    name = forms.CharField(label='Name & Surname', max_length=50, required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control',
                                                         'placeholder': 'Name Surname'}))
    company_name = forms.CharField(label='Company Name', max_length=100, required=False,
                                   widget=forms.TextInput(attrs={'class': 'form-control',
                                                                 'placeholder': 'Company'}))

    def __init__(self, readonly=False, *args, **kwargs):
        super(AdvertiserEditForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['email'].widget.attrs['readonly'] = readonly
            self.fields['phone'].widget.attrs['readonly'] = readonly
            self.fields['name'].widget.attrs['readonly'] = readonly
            self.fields['company_name'].widget.attrs['readonly'] = readonly

    class Meta:
        model = Advertiser
        fields = ('email', 'phone', 'name', 'company_name')


class Account(forms.Form):
    email = forms.CharField(label='Email', max_length=50)
    phone = forms.CharField(label='Phone', max_length=50)
    description = forms.CharField(label='Description', max_length=50, required=False)
    name = forms.CharField(label='Name & Surname', max_length=50, required=False)
    company_name = forms.CharField(label='Company Name', max_length=100, required=False)


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

