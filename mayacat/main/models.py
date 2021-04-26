from django.db import models
from django.conf import settings
from django.urls import reverse
import uuid
from django.contrib.auth.models import User

# Create your models here
"""
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

"""

class Student(User):
    phone = models.CharField(max_length=50, blank=True)
    description = models.TextField()


class Instructor(User):
    phone = models.CharField(max_length=50, blank=True)
    description = models.TextField()

    def __str__(self):
        return "".format("Instructor: ", self.username)


class SiteAdmin(User):
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
        return reverse('main:desc', kwargs={'slug':self.slug})

    # so that we can call it as course.lecture_list() directly
    @property
    def lecture_list(self):
        print(self.lecture_set)
        return self.lecture_set.all().order_by('lecture_name')

class Gift(models.Model):
    # added a gift-id because Django does not support composite primary keys with 2+ columns
    gift_id = models.UUIDField(primary_key=True, max_length=32, editable=False, default=uuid.uuid4)

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='receiver')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)


class Complaint(models.Model):
    comp_id = models.UUIDField(primary_key=True, max_length=32, editable=False, default=uuid.uuid4)
    s_user = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    creation_date = models.DateField(auto_created=True)

    description = models.TextField()


class Lecture(models.Model):
    lecture_no = models.UUIDField(primary_key=True, max_length=32, default=uuid.uuid4, editable=False)

    lecture_name = models.CharField(max_length=200)
    # position = models.IntegerField()

    lecture_slug = models.SlugField()
    ### video_file = models.FileField() veya
    video_url = models.CharField(max_length=200)

    cno = models.ForeignKey(Course, on_delete=models.CASCADE)

    def get_url(self):
        return reverse('main:lecture-detail',
                       kwargs={
                           'course_slug': self.cno.slug,
                           'lecture_slug': self.lecture_slug
                       })

    def __str__(self):
        return self.lecture_name

class Takes_note(models.Model):
    # new primary key because Django does not support composite primary keys
    note_id = models.UUIDField(primary_key=True, max_length=32, editable=False, default=uuid.uuid4)

    s_username = models.ForeignKey(Student, on_delete=models.CASCADE)
    lecture_no = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    note = models.TextField()


class Wishes(models.Model):
    # new primary key because Django does not support composite primary keys
    wishes_id = models.UUIDField(primary_key=True, max_length=32, editable=False, default=uuid.uuid4)

    user = models.ForeignKey(Student, on_delete=models.CASCADE)
    cno = models.ForeignKey(Course, on_delete=models.CASCADE)


class Finishes(models.Model):
    # new primary key because Django does not support composite primary keys
    finishes_id = models.UUIDField(primary_key=True, max_length=32, editable=False, default=uuid.uuid4)

    user = models.ForeignKey(Student, on_delete=models.CASCADE)
    cno = models.ForeignKey(Course, on_delete=models.CASCADE)

    comment = models.TextField(blank=True)


class Rate(models.Model):
    # new primary key because Django does not support composite primary keys
    finishes_id = models.UUIDField(primary_key=True, max_length=32, editable=False, default=uuid.uuid4)

    user = models.ForeignKey(Student, on_delete=models.CASCADE)
    cno = models.ForeignKey(Course, on_delete=models.CASCADE)

    score = models.PositiveSmallIntegerField()  # we can add a limit to this


class Enroll(models.Model):
    # new primary key because Django does not support composite primary keys
    enroll_id = models.UUIDField(primary_key=True, max_length=32, editable=False, default=uuid.uuid4)

    user = models.ForeignKey(Student, on_delete=models.CASCADE)
    cno = models.ForeignKey(Course, on_delete=models.CASCADE)


class Announcement(models.Model):
    # new primary key because Django does not support composite primary keys
    ann_id = models.UUIDField(primary_key=True, max_length=32, editable=False, default=uuid.uuid4)

    i_user = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    cno = models.ForeignKey(Course, on_delete=models.CASCADE)

    ann_text = models.TextField()
    ann_date = models.DateField(auto_created=True)


class Contributor(models.Model):
    # new primary key because Django does not support composite primary keys
    cont_id = models.UUIDField(primary_key=True, max_length=32, editable=False, default=uuid.uuid4)

    user = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    cno = models.ForeignKey(Course, on_delete=models.CASCADE)


class Progress(models.Model):
    # new primary key because Django does not support composite primary keys
    prog_id = models.UUIDField(primary_key=True, max_length=32, editable=False, default=uuid.uuid4)

    s_username = models.ForeignKey(Student, on_delete=models.CASCADE)
    lecture_no = models.ForeignKey(Lecture, on_delete=models.CASCADE)


class Teaches(models.Model):
    # new primary key because Django does not support composite primary keys
    teach_id = models.UUIDField(primary_key=True, max_length=32, editable=False, default=uuid.uuid4)

    user = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    lecture_no = models.ForeignKey(Lecture, on_delete=models.CASCADE)


class Topic(models.Model):
    topicname = models.CharField(primary_key=True, max_length=100)


class Course_Topic(models.Model):
    # new primary key because Django does not support composite primary keys
    course_topic_id = models.UUIDField(primary_key=True, max_length=32, editable=False, default=uuid.uuid4)

    cno = models.ForeignKey(Course, on_delete=models.CASCADE)
    topicname = models.ForeignKey(Topic, on_delete=models.CASCADE)


class Interested_in(models.Model):
    # new primary key because Django does not support composite primary keys
    interested_in_id = models.UUIDField(primary_key=True, max_length=32, editable=False, default=uuid.uuid4)

    cno = models.ForeignKey(Course, on_delete=models.CASCADE)
    s_username = models.ForeignKey(Student, on_delete=models.CASCADE)


class Discount(models.Model):
    discountno = models.UUIDField(primary_key=True, max_length=32, editable=False, default=uuid.uuid4)

    cno = models.ForeignKey(Course, on_delete=models.CASCADE)
    admin_username = models.ForeignKey(SiteAdmin, on_delete=models.CASCADE)

    newprice = models.DecimalField(max_digits=6, decimal_places=2)
    startdate = models.DateTimeField(auto_created=True)
    finishdate = models.DateTimeField()

    situation = models.SmallIntegerField()


class Post(models.Model):
    postno = models.UUIDField(primary_key=True, max_length=32, editable=False, default=uuid.uuid4)

    lecture_no = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    username = models.ForeignKey(User, on_delete=models.CASCADE)

    post = models.TextField()


class Quest_answ(models.Model):
    answer_no = models.ForeignKey(Post, primary_key=True, related_name='answer', on_delete=models.CASCADE)
    question_no = models.ForeignKey(Post, related_name='question', on_delete=models.CASCADE)


class Advertisement(models.Model):
    advertisementno = models.UUIDField(primary_key=True, max_length=32, editable=False, default=uuid.uuid4)

    ad_username = models.ForeignKey(Advertiser, on_delete=models.CASCADE)
    cno = models.ForeignKey(Course, on_delete=models.CASCADE)

    advertisement = models.CharField(max_length=512)
    status = models.SmallIntegerField()
    payment = models.DecimalField(max_digits=20, decimal_places=2)
    startdate = models.DateField()
    finishdate = models.DateField()


class RefundRequest(models.Model):
    refund_id = models.UUIDField(primary_key=True, max_length=32, editable=False, default=uuid.uuid4)

    s_username = models.ForeignKey(Student, on_delete=models.CASCADE)
    cno = models.ForeignKey(Course, on_delete=models.CASCADE)

    reason = models.CharField(max_length=500)

    status = models.SmallIntegerField(default=0)


class Evaluates(models.Model):
    refund_id = models.ForeignKey(RefundRequest, primary_key=True, on_delete=models.CASCADE, default=uuid.uuid4)
    admin_username = models.ForeignKey(SiteAdmin, on_delete=models.CASCADE)

    reply_date = models.DateField()


class Assignment(models.Model):
    assignmentno = models.UUIDField(primary_key=True, max_length=32, editable=False, default=uuid.uuid4)

    lecture_no = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    assignment = models.FileField(upload_to='lecture/assignments/')


class LectureMaterial(models.Model):
    materialno = models.UUIDField(primary_key=True, max_length=32, editable=False, default=uuid.uuid4)
    lecture_no = models.ForeignKey(Lecture, on_delete=models.CASCADE)

    material = models.FileField(upload_to='lecture/material/')


class Inside_Cart(models.Model):
    # new primary key because Django does not support composite primary keys
    inside_cart_id = models.UUIDField(primary_key=True, max_length=32, editable=False, default=uuid.uuid4)

    cno = models.ForeignKey(Course, on_delete=models.CASCADE)
    username = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer')
    receiver_username = models.ForeignKey(Student, on_delete=models.CASCADE, blank=True,
                                          related_name='insidecart_receiver')
