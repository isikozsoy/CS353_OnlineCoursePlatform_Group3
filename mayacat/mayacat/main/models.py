from django.db import models
# from django.contrib.auth.models import User
from django.conf import settings
import uuid


# Create your models here

class User(models.Model):
    username = models.CharField(
        max_length=50,
        primary_key=True)
    name = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)

    def __str__(self):
        return self.username


class Student(User):
    description = models.TextField()


class Instructor(User):
    description = models.TextField()

    def __str__(self):
        return "".format("Instructor: ", self.username)


class Admin(User):
    ssn = models.CharField(max_length=20)
    address = models.CharField(max_length=100)


class Advertiser(models.Model):
    ad_username = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    company_name = models.CharField(max_length=100)
    email = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)


class Course(models.Model):
    cno = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    cname = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=6, decimal_places=2) # up to 9999 with 2 decimal places

    ######### WE CAN CHANGE THE BELOW ENUMERATION AS SMALLINTEGERFIELD
    class Situation(models.TextChoices):
        Pnd = 'Pending'
        Dcl = 'Declined'
        Appr = 'Approved'

    situation = models.CharField(
        max_length=8,
        choices=Situation.choices,
        default=Situation.Pnd,
    )

    is_private = models.BooleanField(default=False)

    course_img = models.ImageField(upload_to='thumbnails/')  ## varchar 512

    description = models.TextField()


class Gift(models.Model):
    # added a gift-id because Django does not support composite primary keys with 2+ columns
    gift_id = models.UUIDField(primary_key=True, max_length=32, editable=False)

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='receiver')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)


class Complaint(models.Model):
    comp_id = models.UUIDField(primary_key=True, max_length=32, editable=False)
    s_user = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    creation_date = models.DateField(auto_now_add=True)

    description = models.TextField()


"""
"""
