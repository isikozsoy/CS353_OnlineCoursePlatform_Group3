import sys

from django import forms
from django.db import connection, Error

from .models import Course


class Checkout(forms.Form):
    card_name = forms.CharField(label='Card Name', max_length=26, min_length=2, required=True)
    card_number = forms.CharField(label='Card Number', max_length=16, required=True)
    expiry_date = forms.CharField(label='Expiry Date', max_length=5, required=True)  # will be worked on
    security_code = forms.CharField(label='Security Code', max_length=3, required=True)


class Trash(forms.Form):
    course_slug = forms.CharField(label='Course Slug', max_length=50)


class GiftForm(forms.Form):
    receiver_id = forms.CharField(label='Receiver Username:', max_length=150)
    item_id = forms.CharField(widget=forms.HiddenInput())


class CoursesDiscount(forms.Form):
    def __init__(self, *args, **kwargs):
        self.instructor_id = kwargs.pop('instructor_id')
        super(CoursesDiscount, self).__init__(*args, **kwargs)
        cursor = connection.cursor()
        try:
            cursor.execute('select cno '
                           'from courses_course '
                           'where owner_id = %s and new_price is null and is_private = 0;', [self.instructor_id])
            qset = Course.objects.filter(cno__in=(x[0] for x in cursor))
            self.fields['courses'] = forms.ModelMultipleChoiceField(
                qset,
                widget=forms.CheckboxSelectMultiple(attrs={'class': 'select', }))
        except Error:
            print('There was an error. ' + str(sys.exc_info()))
        finally:
            cursor.close()
