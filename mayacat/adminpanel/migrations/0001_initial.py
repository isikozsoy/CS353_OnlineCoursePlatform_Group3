# Generated by Django 3.2 on 2021-05-16 16:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Offered_Discount',
            fields=[
                ('discount_id', models.AutoField(primary_key=True, serialize=False)),
                ('creation_date', models.DateField(auto_now_add=True)),
                ('percentage', models.IntegerField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('admin_username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.siteadmin')),
            ],
        ),
    ]
