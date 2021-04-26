from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(SiteAdmin)
admin.site.register(User)
admin.site.register(Student)
admin.site.register(Instructor)
admin.site.register(Course)
admin.site.register(Lecture)
admin.site.register(LectureMaterial)
admin.site.register(Wishes)
