import sys

from django.db import connection, DatabaseError, Error
from django.http import HttpResponseRedirect


def create_trigger():
    cursor_ = connection.cursor()

    try:
        cursor_.execute('drop trigger if exists insert_average;')
        cursor_.execute('create trigger insert_average after insert on main_finishes for each row '
                        'begin '
                        'insert into main_avg_rate (avg, cno_id) values (new.score, new.cno_id) '
                        'on duplicate key update avg = (select avg(score) from main_finishes '
                        'where main_finishes.cno_id = new.cno_id);'
                        'end;')
    except DatabaseError:
        print("There was an error.<p> " + str(sys.exc_info()))
    finally:
        cursor_.close()

def create_discount_trigger():
    cursor = connection.cursor()

    try:
        cursor.execute('drop trigger if exists trig;')
        cursor.execute('create trigger trig after insert on main_discount '
                       'for each row '
                       'begin '
                       'update courses_course '
                            'join main_discount md on courses_course.cno = md.cno_id '
                            'join adminpanel_offered_discount aod on md.offerno_id = aod.discount_id '
                       'set new_price = price * (100 - percentage) / 100 '
                       'where courses_course.cno = new.cno_id; '
                       'end;')
    except Error:
        print(sys.exc_info())
    finally:
        cursor.close()

def create_discount_trigger_deletion():
    cursor = connection.cursor()

    try:
        cursor.execute('drop trigger if exists discount_delete_trigger;')
        cursor.execute('create trigger discount_delete_trigger after delete on main_discount '
                       'for each row '
                       'begin '
                            'update courses_course '
                            'set new_price = null '
                            'where courses_course.cno = old.cno_id;'
                       'end;')
    except Error:
        print(sys.exc_info())
    finally:
        cursor.close()

def create_gift_trigger():
    cursor = connection.cursor()

    try:
        cursor.execute('drop trigger if exists insert_gift_enroll;')
        cursor.execute('create trigger insert_gift_enroll after insert on main_gift for each row '
                        'begin '
                        'insert into main_enroll (cno_id, user_id) values (new.course_id, new.receiver_id); '
                        'end;')
    except Error:
        print(sys.exc_info())
    finally:
        cursor.close()