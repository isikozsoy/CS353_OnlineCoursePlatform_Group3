# Generated by Django 3.2 on 2021-04-28 20:09

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('cno', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('cname', models.CharField(max_length=50)),
                ('price', models.DecimalField(decimal_places=2, max_digits=6)),
                ('slug', models.SlugField()),
                ('situation', models.CharField(choices=[('Pending', 'Pnd'), ('Declined', 'Dcl'), ('Approved', 'Appr')], default='Pending', max_length=8)),
                ('is_private', models.BooleanField(default=False)),
                ('course_img', models.ImageField(upload_to='thumbnails/')),
                ('description', models.TextField()),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.instructor')),
            ],
        ),
        migrations.CreateModel(
            name='Lecture',
            fields=[
                ('lecture_no', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('lecture_name', models.CharField(max_length=200)),
                ('lecture_slug', models.SlugField()),
                ('video_url', models.CharField(max_length=200)),
                ('cno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.course')),
            ],
        ),
        migrations.CreateModel(
            name='LectureMaterial',
            fields=[
                ('materialno', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('material', models.FileField(upload_to='lecture/material/')),
                ('lecture_no', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.lecture')),
            ],
        ),
    ]
