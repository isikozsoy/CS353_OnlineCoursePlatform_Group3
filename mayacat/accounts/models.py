from django.db import models
from django.contrib.auth.models import User
import uuid


class Student(User):
    phone = models.CharField(max_length=50, blank=True)
    description = models.TextField()
    type = "student"


class Instructor(User):
    phone = models.CharField(max_length=50, blank=True)
    description = models.TextField()
    type = "instructor"

    def __str__(self):
        return "".format("Instructor: ", self.username)


class SiteAdmin(User):
    ssn = models.CharField(max_length=20)
    address = models.CharField(max_length=100)
    type = "admin"


class Advertiser(User):
    name = models.CharField(max_length=50)
    company_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=50)
    type = "advertiser"
