from django.contrib import admin
from .models import *

# Register your models here.

# admins have access to which tables
admin.site.register(SiteAdmin)
admin.site.register(Evaluates)

admin.site.register(User)
admin.site.register(Student)
admin.site.register(Instructor)
admin.site.register(Advertiser)
