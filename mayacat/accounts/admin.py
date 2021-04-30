from django.contrib import admin
from django.db import connection

username = "defne_admin"
email = "defneciftci00@gmail.com"

#connection.execute('insert into auth_user (password, is_superuser, username, email, is_staff, is_active) '
#                   'values (password, 1, %s, %s, 1, 1);', [username, email])


# Register your models here.
