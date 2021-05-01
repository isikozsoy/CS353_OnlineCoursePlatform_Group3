from django import forms


class GiftInfo(forms.Form):
    username = forms.CharField(label='Username', max_length=50)