from django.db import models
from accounts.models import SiteAdmin


class Offered_Discount(models.Model):
    discount_id = models.AutoField(primary_key=True)
    creation_date = models.DateField(auto_now_add=True)
    percentage = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    admin_username = models.ForeignKey(SiteAdmin, on_delete=models.CASCADE)
