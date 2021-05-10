from django.forms import forms


class SiteAdminSaveForm(forms.Form):
    ssn = forms.CharField(label='Social Security Number', max_length=20, widget=forms.TextInput)
    address = forms.CharField(label='Address', max_length=100, widget=forms.TextInput)