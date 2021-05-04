from django import forms

class AskQuestion(forms.Form):
    question = forms.CharField(label='question', max_length=500)