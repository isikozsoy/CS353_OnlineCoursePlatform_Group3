# Generated by Django 3.2 on 2021-05-16 16:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0001_initial'),
        ('courses', '0001_initial'),
        ('adminpanel', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Avg_Rate',
            fields=[
                ('cno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='courses.course')),
                ('avg', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('postno', models.AutoField(primary_key=True, serialize=False)),
                ('post', models.TextField()),
                ('date', models.DateField(auto_now_add=True)),
                ('lecture_no', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.lecture')),
                ('username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RefundRequest',
            fields=[
                ('refund_id', models.AutoField(primary_key=True, serialize=False)),
                ('reason', models.CharField(max_length=500)),
                ('status', models.SmallIntegerField(default=0)),
                ('date', models.DateField(auto_now_add=True)),
                ('cno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.course')),
                ('s_username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.student')),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('topicname', models.CharField(max_length=100, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Wishes',
            fields=[
                ('wishes_id', models.AutoField(primary_key=True, serialize=False)),
                ('cno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.student')),
            ],
        ),
        migrations.CreateModel(
            name='Teaches',
            fields=[
                ('teach_id', models.AutoField(primary_key=True, serialize=False)),
                ('lecture_no', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.lecture')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.instructor')),
            ],
        ),
        migrations.CreateModel(
            name='Takes_note',
            fields=[
                ('note_id', models.AutoField(primary_key=True, serialize=False)),
                ('note', models.TextField()),
                ('lecture_no', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.lecture')),
                ('s_username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.student')),
            ],
        ),
        migrations.CreateModel(
            name='Progress',
            fields=[
                ('prog_id', models.AutoField(primary_key=True, serialize=False)),
                ('lecture_no', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.lecture')),
                ('s_username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.student')),
            ],
        ),
        migrations.CreateModel(
            name='Interested_in',
            fields=[
                ('interested_in_id', models.AutoField(primary_key=True, serialize=False)),
                ('s_username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.student')),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.topic')),
            ],
        ),
        migrations.CreateModel(
            name='Inside_Cart',
            fields=[
                ('inside_cart_id', models.AutoField(primary_key=True, serialize=False)),
                ('cno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.course')),
                ('receiver_username', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='insidecart_receiver', to='accounts.student')),
                ('username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buyer', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Gift',
            fields=[
                ('gift_id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.course')),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to='accounts.student')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Finishes',
            fields=[
                ('finishes_id', models.AutoField(primary_key=True, serialize=False)),
                ('comment', models.TextField(blank=True, null=True)),
                ('score', models.PositiveSmallIntegerField(default=0)),
                ('cno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.student')),
            ],
        ),
        migrations.CreateModel(
            name='Enroll',
            fields=[
                ('enroll_id', models.AutoField(primary_key=True, serialize=False)),
                ('cno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.student')),
            ],
        ),
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('discountno', models.AutoField(primary_key=True, serialize=False)),
                ('cno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.course')),
                ('offerno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminpanel.offered_discount')),
            ],
        ),
        migrations.CreateModel(
            name='Course_Topic',
            fields=[
                ('course_topic_id', models.AutoField(primary_key=True, serialize=False)),
                ('cno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.course')),
                ('topicname', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.topic')),
            ],
        ),
        migrations.CreateModel(
            name='Contributor',
            fields=[
                ('cont_id', models.AutoField(primary_key=True, serialize=False)),
                ('cno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.instructor')),
            ],
        ),
        migrations.CreateModel(
            name='Complaint',
            fields=[
                ('creation_date', models.DateField(auto_created=True)),
                ('comp_id', models.AutoField(primary_key=True, serialize=False)),
                ('description', models.TextField()),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.course')),
                ('s_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.student')),
            ],
        ),
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('assignmentno', models.AutoField(primary_key=True, serialize=False)),
                ('assignment', models.FileField(upload_to='lecture/assignments/')),
                ('lecture_no', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.lecture')),
            ],
        ),
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('ann_date', models.DateField(auto_created=True)),
                ('ann_id', models.AutoField(primary_key=True, serialize=False)),
                ('ann_text', models.TextField()),
                ('cno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.course')),
                ('i_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.instructor')),
            ],
        ),
        migrations.CreateModel(
            name='Advertisement',
            fields=[
                ('advertisementno', models.AutoField(primary_key=True, serialize=False)),
                ('advertisement', models.CharField(max_length=512)),
                ('status', models.SmallIntegerField()),
                ('payment', models.DecimalField(decimal_places=2, max_digits=20)),
                ('startdate', models.DateField()),
                ('finishdate', models.DateField()),
                ('ad_username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.advertiser')),
                ('cno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.course')),
            ],
        ),
        migrations.CreateModel(
            name='Quest_answ',
            fields=[
                ('answer_no', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='answer', serialize=False, to='main.post')),
                ('question_no', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='question', to='main.post')),
            ],
        ),
        migrations.CreateModel(
            name='Evaluates',
            fields=[
                ('refund_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='main.refundrequest')),
                ('reply_date', models.DateField()),
                ('admin_username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.siteadmin')),
            ],
        ),
    ]
