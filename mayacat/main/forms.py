from django import forms
from .models import Course

class Checkout(forms.Form):
    card_name = forms.CharField(label='Card Name', max_length = 26, min_length = 2)
    card_number = forms.CharField(label='Card Number', max_length = 16)
    expiry_date = forms.CharField(label='Expiry Date', max_length = 5) # will be worked on
    security_code = forms.CharField(label='Security Code', max_length = 3)
