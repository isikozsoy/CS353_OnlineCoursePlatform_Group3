from django.contrib import admin
from .models import *
from courses.models import *

# Register your models here.
admin.site.register(Student)
admin.site.register(Instructor)
admin.site.register(Course)
admin.site.register(Lecture)
admin.site.register(LectureMaterial)
admin.site.register(Wishes)
admin.site.register(Gift)
admin.site.register(Announcement)