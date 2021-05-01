from django import forms


class ComplainForm(forms.Form):
    description = forms.CharField(label='Description', max_length=1000)

