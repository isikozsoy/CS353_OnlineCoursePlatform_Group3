from django.db import connection, DatabaseError
from django.http import HttpResponseRedirect


def create_trigger():
    cursor_ = connection.cursor()

    try:
        cursor_.execute('create trigger insert_average after insert on main_finishes for each row '
                        'begin '
                        'insert into main_avg_rate (avg, cno_id) values (new.score, new.cno_id) '
                        'on duplicate key update avg = (select avg(score) from main_finishes '
                        'where main_finishes.cno_id = new.cno_id);'
                        'end;')
    except DatabaseError:
        print("An error occurred.")
        HttpResponseRedirect('/')
    finally:
        cursor_.close()
