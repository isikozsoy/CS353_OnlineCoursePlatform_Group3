from django.db import models
from main.models import *
from accounts.models import Instructor


# Create your models here.
class Course(models.Model):
    cno = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, max_length=32)
    owner = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    cname = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=6, decimal_places=2)  # up to 9999 with 2 decimal places

    slug = models.SlugField()

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

    def __str__(self):
        return self.cname

    def get_url(self):
        return reverse('courses:desc', kwargs={'slug': self.slug})

    # so that we can call it as course.lecture_list() directly
    @property
    def lecture_list(self):
        print(self.lecture_set)
        return self.lecture_set.all().order_by('lecture_name')

class Lecture(models.Model):
    lecture_no = models.UUIDField(primary_key=True, max_length=32, default=uuid.uuid4, editable=False)

    lecture_name = models.CharField(max_length=200)
    # position = models.IntegerField()

    lecture_slug = models.SlugField()
    ### video_file = models.FileField() veya
    video_url = models.CharField(max_length=200)

    cno = models.ForeignKey(Course, on_delete=models.CASCADE)

    def get_url(self):
        return reverse('courses:lecture-detail',
                       kwargs={
                           'course_slug': self.cno.slug,
                           'lecture_slug': self.lecture_slug
                       })

    def __str__(self):
        return self.lecture_name

class LectureMaterial(models.Model):
    materialno = models.UUIDField(primary_key=True, max_length=32, editable=False, default=uuid.uuid4)
    lecture_no = models.ForeignKey(Lecture, on_delete=models.CASCADE)

    material = models.FileField(upload_to='lecture/material/')