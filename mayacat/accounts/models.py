from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
import uuid

"""
    - All Users have username, email, and passwords as default.
    - Django's official User authentication class is used for User. The below roles are extensions of this class.
    - Every User is a Student by default. The user can choose to be an instructor or an advertiser later on.
    - type: 0 for (only) Student, 1 for Instructor, 2 for Advertiser, 3 for SiteAdmin
"""

class DefaultUser(User):
    password_orig = models.CharField(max_length=50)
    type = models.IntegerField()

class Student(DefaultUser):
    phone = models.CharField(max_length=50, blank=True)


class Instructor(Student):
    description = models.TextField()

    def __str__(self):
        return self.username


class Advertiser(DefaultUser):
    name = models.CharField(max_length=50)
    company_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=50)

class SiteAdmin(DefaultUser):
    ssn = models.CharField(max_length=20)
    address = models.CharField(max_length=100)