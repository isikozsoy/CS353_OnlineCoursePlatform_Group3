# Generated by Django 3.2 on 2021-05-10 23:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20210507_1529'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evaluates',
            name='reply_date',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.RemoveField(
            model_name='interested_in',
            name='cno',
        ),
        migrations.AddField(
            model_name='interested_in',
            name='topic',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='main.topic'),
            preserve_default=False,
        ),
    ]
