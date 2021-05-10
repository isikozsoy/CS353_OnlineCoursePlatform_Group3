from django import forms


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
