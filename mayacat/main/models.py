from django.db import models
from django.conf import settings
from django.urls import reverse
import datetime
from courses.models import *
from accounts.models import *


class Gift(models.Model):
    # added a gift-id because Django does not support composite primary keys with 2+ columns
    gift_id = models.AutoField(primary_key=True)

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='receiver')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)


class Complaint(models.Model):
    comp_id = models.AutoField(primary_key=True)
    s_user = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    creation_date = models.DateField(auto_created=True)

    description = models.TextField()


class Takes_note(models.Model):
    # new primary key because Django does not support composite primary keys
    note_id = models.AutoField(primary_key=True)

    s_username = models.ForeignKey(Student, on_delete=models.CASCADE)
    lecture_no = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    note = models.TextField()


class Wishes(models.Model):
    # new primary key because Django does not support composite primary keys
    wishes_id = models.AutoField(primary_key=True)

    user = models.ForeignKey(Student, on_delete=models.CASCADE)
    cno = models.ForeignKey(Course, on_delete=models.CASCADE)

    def get_url(self):
        return reverse('main:wishlist_items')


class Finishes(models.Model):
    # new primary key because Django does not support composite primary keys
    finishes_id = models.AutoField(primary_key=True)

    user = models.ForeignKey(Student, on_delete=models.CASCADE)
    cno = models.ForeignKey(Course, on_delete=models.CASCADE)

    comment = models.TextField(blank=True, null=True)
    score = models.PositiveSmallIntegerField(default=0)


class Enroll(models.Model):
    # new primary key because Django does not support composite primary keys
    enroll_id = models.AutoField(primary_key=True)

    user = models.ForeignKey(Student, on_delete=models.CASCADE)
    cno = models.ForeignKey(Course, on_delete=models.CASCADE)


class Announcement(models.Model):
    # new primary key because Django does not support composite primary keys
    ann_id = models.AutoField(primary_key=True)

    i_user = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    cno = models.ForeignKey(Course, on_delete=models.CASCADE)

    ann_text = models.TextField()
    ann_date = models.DateField(auto_created=True)


class Contributor(models.Model):
    # new primary key because Django does not support composite primary keys
    cont_id = models.AutoField(primary_key=True)

    user = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    cno = models.ForeignKey(Course, on_delete=models.CASCADE)


class Progress(models.Model):
    # new primary key because Django does not support composite primary keys
    prog_id = models.AutoField(primary_key=True)

    s_username = models.ForeignKey(Student, on_delete=models.CASCADE)
    lecture_no = models.ForeignKey(Lecture, on_delete=models.CASCADE)


class Teaches(models.Model):
    # new primary key because Django does not support composite primary keys
    teach_id = models.AutoField(primary_key=True)

    user = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    lecture_no = models.ForeignKey(Lecture, on_delete=models.CASCADE)


class Topic(models.Model):
    topicname = models.CharField(primary_key=True, max_length=100)


class Course_Topic(models.Model):
    # new primary key because Django does not support composite primary keys
    course_topic_id = models.AutoField(primary_key=True)

    cno = models.ForeignKey(Course, on_delete=models.CASCADE)
    topicname = models.ForeignKey(Topic, on_delete=models.CASCADE)


class Interested_in(models.Model):
    # new primary key because Django does not support composite primary keys
    interested_in_id = models.AutoField(primary_key=True)

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    s_username = models.ForeignKey(Student, on_delete=models.CASCADE)


class Discount(models.Model):
    discountno = models.AutoField(primary_key=True)

    cno = models.ForeignKey(Course, on_delete=models.CASCADE)
    admin_username = models.ForeignKey(SiteAdmin, on_delete=models.CASCADE)

    newprice = models.DecimalField(max_digits=6, decimal_places=2)
    startdate = models.DateTimeField(auto_created=True)
    finishdate = models.DateTimeField()

    situation = models.SmallIntegerField()


class Post(models.Model):
    postno = models.AutoField(primary_key=True)

    lecture_no = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    username = models.ForeignKey(User, on_delete=models.CASCADE)

    post = models.TextField()


class Quest_answ(models.Model):
    answer_no = models.ForeignKey(Post, primary_key=True, related_name='answer',
                                  on_delete=models.CASCADE)
    question_no = models.ForeignKey(Post, related_name='question', on_delete=models.CASCADE)


class Advertisement(models.Model):
    advertisementno = models.AutoField(primary_key=True)

    ad_username = models.ForeignKey(Advertiser, on_delete=models.CASCADE)
    cno = models.ForeignKey(Course, on_delete=models.CASCADE)

    advertisement = models.CharField(max_length=512)
    status = models.SmallIntegerField()
    payment = models.DecimalField(max_digits=20, decimal_places=2)
    startdate = models.DateField()
    finishdate = models.DateField()


class RefundRequest(models.Model):
    refund_id = models.AutoField(primary_key=True)

    s_username = models.ForeignKey(Student, on_delete=models.CASCADE)
    cno = models.ForeignKey(Course, on_delete=models.CASCADE)

    reason = models.CharField(max_length=500)

    status = models.SmallIntegerField(default=0)


class Evaluates(models.Model):
    refund_id = models.ForeignKey(RefundRequest, primary_key=True, on_delete=models.CASCADE)
    admin_username = models.ForeignKey(SiteAdmin, on_delete=models.CASCADE)

    reply_date = models.DateField()


class Assignment(models.Model):
    assignmentno = models.AutoField(primary_key=True)

    lecture_no = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    assignment = models.FileField(upload_to='lecture/assignments/')


class Inside_Cart(models.Model):
    # new primary key because Django does not support composite primary keys
    inside_cart_id = models.AutoField(primary_key=True)

    cno = models.ForeignKey(Course, on_delete=models.CASCADE)
    username = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer')
    receiver_username = models.ForeignKey(Student, on_delete=models.CASCADE, blank=True, null=True,
                                          related_name='insidecart_receiver')
