from django import forms


class ComplainForm(forms.Form):
    description = forms.CharField(label='Description', max_length=1000)


class GiftInfo(forms.Form):
    username = forms.CharField(label='Username', max_length=50)