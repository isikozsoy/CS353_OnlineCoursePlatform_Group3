from django import forms
from .models import *


class AccountViewForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user_type = kwargs.pop('user_type')
        self.user = kwargs.pop('user')
        self.readonly = kwargs.pop('readonly')
        super(AccountViewForm, self).__init__(*args, **kwargs)

        self.fields['email'] = forms.CharField(label='Email', max_length=50, required=False,
                                               widget=forms.TextInput(attrs={'class': 'form-control',
                                                                             'placeholder': self.user.email}))
        self.fields['email'].widget.attrs['readonly'] = self.readonly

        if self.user_type != 3:  # only admins do not have a phone recorded
            self.fields['phone'] = forms.CharField(label='Phone number', max_length=50, required=False,
                                                   widget=forms.TextInput(attrs={'class': 'form-control',
                                                                                 'placeholder': self.user.phone}))
            self.fields['phone'].widget.attrs['readonly'] = self.readonly

        if self.user_type == 2:  # advertiser
            self.fields['name'] = forms.CharField(label='Phone number', max_length=50, required=False,
                                                  widget=forms.TextInput(attrs={'class': 'form-control',
                                                                                'placeholder': self.user.name}))
            self.fields['company_name'] = forms.CharField(label='Company Name', max_length=100, required=False,
                                                          widget=forms.TextInput(attrs={'class': 'form-control',
                                                                                        'placeholder': self.user.company_name}))
            self.fields['name'].widget.attrs['readonly'] = self.readonly
            self.fields['company_name'].widget.attrs['readonly'] = self.readonly
        elif self.user_type == 1:  # instructor
            self.fields['description'] = forms.CharField(label='Description', max_length=1000, required=False,
                                                         widget=forms.TextInput(attrs={'class': 'form-control',
                                                                                       'placeholder': self.user.description}))
            self.fields['description'].widget.attrs['readonly'] = self.readonly
        elif self.user_type == 3:  # site admin
            self.fields['ssn'] = forms.CharField(label='SSN', max_length=20, required=False,
                                                 widget=forms.TextInput(attrs={'class': 'form-control',
                                                                               'placeholder': self.user.ssn}))
            self.fields['address'] = forms.CharField(label='Description', max_length=20, required=False,
                                                     widget=forms.TextInput(attrs={'class': 'form-control',
                                                                                   'placeholder': self.user.address}))


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

    first_name = forms.CharField(label='First name', max_length=150)
    last_name = forms.CharField(label='Last name', max_length=150)
    description = forms.CharField(label='Description', max_length=1000, required=False)

    name = forms.CharField(label='Name & Surname', max_length=50, required=False)
    company_name = forms.CharField(label='Company Name', max_length=50, required=False)

    password = forms.CharField(label='Password', max_length=50, widget=forms.PasswordInput)
