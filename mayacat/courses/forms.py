from django import forms


class ComplainForm(forms.Form):
    description = forms.CharField(label='Description', max_length=1000)


class GiftInfo(forms.Form):
    username = forms.CharField(label='Username', max_length=50)


TOPIC_CHOICES = (
    ("1", "Design"),
    ("2", "Development"),
    ("3", "Marketing"),
    ("4", "IT and Software"),
    ("5", "Personal Development"),
    ("6", "Business"),
    ("7", "Music"),
    ("8", "Other"),
)


class CreateCourseForm(forms.Form):
    cname = forms.CharField(label='Course Name', max_length=50)
    price = forms.DecimalField(label='Price', max_digits=6, decimal_places=2)
    topic = forms.ChoiceField(label='Topic', choices=TOPIC_CHOICES)

    thumbnail = forms.ImageField()

    description = forms.CharField(max_length=4000, widget=forms.TextInput())

    private = forms.BooleanField(label='Private?')
