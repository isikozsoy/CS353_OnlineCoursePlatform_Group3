from django.shortcuts import render, redirect
from django.db import connection
from django.http import HttpResponse, HttpResponseRedirect
import uuid

from django.views.generic import ListView, DetailView, View
from .models import *
from accounts.models import *

cursor = connection.cursor()


class WishlistView(ListView):
    def get(self, request):
        # WILL BE CHANGED TO CURRENT USER
        user_id = request.user.id
        wishlist_q = Wishes.objects.raw('''SELECT *
                                            FROM main_wishes
                                            WHERE user_id = %s''', [user_id])

        cursor = connection.cursor()
        cursor.execute('select type '
                       'from auth_user '
                       'inner join accounts_defaultuser ad on auth_user.id = ad.user_ptr_id '
                       'where id = %s;', [request.user.id])

        row = cursor.fetchone()
        user_type = -1
        if row:
            user_type = row[0]

        context = {
            'wishlist_q': wishlist_q,
            'user_type': user_type
        }
        return render(request, 'main/wishlist.html', context)

class OffersView(ListView):
    def get(self, request):
        # WILL BE CHANGED TO CURRENT USER
        user_id = request.user.id
        offers_q = Advertisement.objects.raw('''SELECT *
                                            FROM main_advertisement
                                            WHERE ad_username_id = %s''', [user_id])

        cursor = connection.cursor()
        cursor.execute('select type '
                       'from auth_user '
                       'inner join accounts_defaultuser ad on auth_user.id = ad.user_ptr_id '
                       'where id = %s;', [request.user.id])

        row = cursor.fetchone()
        user_type = -1
        if row:
            user_type = row[0]

        context = {
            'offers_q': offers_q,
            'user_type': user_type
        }
        return render(request, 'main/offers.html', context)


def add_to_wishlist(request, course_slug):
    course = Course.objects.raw('SELECT * FROM courses_course WHERE slug = %s LIMIT 1', [course_slug])[0]
    cno = course.cno

    # WILL BE CHANGED TO CURRENT USER
    user_id = request.user.id
    cursor = connection.cursor()

    current_wishes = Wishes.objects.raw('SELECT * FROM main_wishes WHERE cno_id = %s AND user_id = %s',
                                        [cno, user_id])

    if len(list(current_wishes)) == 0:
        cursor.execute('INSERT INTO main_wishes (cno_id, user_id) VALUES (%s, %s);',
                       [cno, user_id])
    else:
        cursor.execute('DELETE FROM main_wishes WHERE cno_id = %s AND user_id = %s', [cno, user_id])

    return redirect("main:wishlist_items")


class MainView(View):
    def get(self, request):
        # TODO: THE COURSES WILL BE CHANGED AS TOP 5 MOST POPULAR AND TOP 5 HIGHEST RATED
        #  also the courses that are not private will be listed here
        cursor = connection.cursor()

        # THE COURSES WILL BE CHANGED AS TOP 5 MOST POPULAR AND TOP 5 HIGHEST RATED
        courses = Course.objects.raw('select * '
                                     'from courses_course;')

        topics = Topic.objects.raw('select * from main_topic order by topicname;')

        cursor.execute('select type '
                       'from auth_user '
                       'inner join accounts_defaultuser ad on auth_user.id = ad.user_ptr_id '
                       'where id = %s;', [request.user.id])

        row = cursor.fetchone()
        user_type = -1
        if row:
            user_type = row[0]

        return render(request, 'main/main.html', {'object_list': courses,
                                                  'topic_list': topics,
                                                  'user_type': user_type})


def course_detail(request, course_id):
    course = Course.objects.raw('SELECT * FROM courses_course WHERE course_id = %s', [course_id])
    # WILL BE CHANGED TO CURRENT USER ?
    user_id = request.user.id
    registered = Enroll.objects.raw('SELECT enroll_id FROM X WHERE user = %s AND cno = %s', [user_id], [course_id])

    lecture_count = Lecture.objects.filter(cno_id=course.cno).count()

    rating = Rate.objects.raw('SELECT AVG(score) FROM X WHERE cno = %s', [course_id])
    advertisement = Advertisement.objects.raw('SELECT advertisement FROM X WHERE cno = %s', [course_id])

    comments = Finishes.objects.raw('SELECT comment FROM X WHERE cno = %s', [course_id])

    cursor = connection.cursor()
    cursor.execute('select type '
                   'from auth_user '
                   'inner join accounts_defaultuser ad on auth_user.id = ad.user_ptr_id '
                   'where id = %s;', [request.user.id])

    row = cursor.fetchone()
    user_type = -1
    if row:
        user_type = row[0]

    return render(request, 'courses/course_detail.html', {'user_type': user_type, 'course': course, 'registered': registered,
                                                       'lecture_count': lecture_count, 'rating': rating,
                                                       'advertisement': advertisement, 'comments': comments})


class ShoppingCartView(View):

    def get(self, request):
        user = request.user

        items_on_cart = Inside_Cart.objects.raw('SELECT * '
                                                'FROM main_inside_cart '
                                                'WHERE username_id = %s;', [user.id]).all()

        items = Course.objects.raw('SELECT * '
                                   'FROM courses_course '
                                   'WHERE cno = %s', [items_on_cart.cno_id])

        # count = Inside_Cart.objects.filter(username=user.name).count()
        count = Inside_Cart.objects.raw('SELECT count(*) '
                                        'FROM main_inside_cart '
                                        'WHERE username_id = %s;', [user.id])

        total_price = Course.objects.raw('SELECT SUM(price) FROM items')

        cursor = connection.cursor()
        cursor.execute('select type '
                       'from auth_user '
                       'inner join accounts_defaultuser ad on auth_user.id = ad.user_ptr_id '
                       'where id = %s;', [request.user.id])

        row = cursor.fetchone()
        user_type = -1
        if row:
            user_type = row[0]

        return render(request, 'main/shopping_cart.html', {'user_type': user_type, 'items': items, 'items_on_cart': items_on_cart,
                                                           'count': count, 'total_price': total_price})


class ShoppingCheckoutView(View):
    def get(self, request):
        cursor = connection.cursor()
        cursor.execute('select type '
                       'from auth_user '
                       'inner join accounts_defaultuser ad on auth_user.id = ad.user_ptr_id '
                       'where id = %s;', [request.user.id])

        row = cursor.fetchone()
        user_type = -1
        if row:
            user_type = row[0]

        return render(request, 'main/checkout.html', {'user_type': user_type})


class NotificationView(View):
    def get(self, request):
        cursor = connection.cursor()
        cursor.execute('select type '
                       'from auth_user '
                       'inner join accounts_defaultuser ad on auth_user.id = ad.user_ptr_id '
                       'where id = %s;', [request.user.id])

        row = cursor.fetchone()
        user_type = -1
        if row:
            user_type = row[0]

        if user_type == 0: # student
            cursor = connection.cursor()
            cursor.execute('SELECT date, cname, username FROM main_gift as G, auth_user as A, courses_course as C'
                           ' WHERE C.cno = G.course_id AND G.sender_id = A.id AND G.receiver_id = %s ORDER BY date DESC'
                           , [request.user.id])
            temp_gift = cursor.fetchall()
            cursor.close()

            gift_arr = []
            for gift in temp_gift:
                gift = list(gift)
                gift.append("gift")
                gift_arr.append(gift)
            print("--------1--------")
            print(gift_arr)
            cursor = connection.cursor()
            cursor.execute('SELECT ann_date, cname, ann_text FROM main_enroll as E, main_announcement A, courses_course C'
                           ' WHERE E.cno_id = A.cno_id AND E.user_id = %s'
                           ' AND E.cno_id = C.cno ORDER BY ann_date DESC', [request.user.id])
            temp_anns = cursor.fetchall()
            cursor.close()

            anns_arr = []
            for ann in temp_anns:
                ann = list(ann)
                ann.append("ann")
                anns_arr.append(ann)
            print("--------2--------")
            print(anns_arr)

            gift_i = 0
            ann_i = 0
            notifications = []
            while gift_i < len(gift_arr) and ann_i < len(anns_arr):
                if anns_arr[ann_i][0] > gift_arr[gift_i][0]:
                    notifications.append(anns_arr[ann_i])
                    ann_i = ann_i + 1
                else:
                    notifications.append(gift_arr[gift_i])
                    gift_i = gift_i + 1

            if gift_i == len(gift_arr):
                while ann_i < len(anns_arr):
                    notifications.append(anns_arr[ann_i])
                    ann_i = ann_i + 1
            elif ann_i == len(anns_arr):
                while gift_i < len(gift_arr):
                    notifications.append(gift_arr[gift_i])
                    gift_i = gift_i + 1

        elif user_type == 1:
            print()
            # blavla
        else:
            print()
        context={'user_type': user_type, 'notifications': notifications}
        return render (request, 'main/notifications.html', context)