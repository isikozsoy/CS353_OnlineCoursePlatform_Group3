# Generated by Django 3.2 on 2021-05-12 11:39

import datetime

import django
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_auto_20210511_1553'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='date',
            field=models.DateField(auto_now_add=True, default=datetime.date.today),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='evaluates',
            name='reply_date',
            field=models.DateField(),
        ),
        migrations.CreateModel(
            name='Avg_Rate',
            fields=[
                ('cno',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False,
                                   to='courses.course')),
                ('avg', models.FloatField()),
            ],
        ),
        migrations.RemoveField(
            model_name='discount',
            name='admin_username',
        ),
        migrations.RemoveField(
            model_name='discount',
            name='finishdate',
        ),
        migrations.RemoveField(
            model_name='discount',
            name='newprice',
        ),
        migrations.RemoveField(
            model_name='discount',
            name='situation',
        ),
        migrations.RemoveField(
            model_name='discount',
            name='startdate',
        ),
        migrations.AddField(
            model_name='discount',
            name='offerno',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE,
                                    to='adminpanel.offered_discount'),
            preserve_default=False,
        ),
    ]
