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
        if request.user.is_authenticated:
            user_id = request.user.id
            gift_not = cursor.execute('SELECT * FROM main_gift WHERE receiver_id = %s ORDER BY date DESC LIMIT 5',
                                         [user_id])
            announcement_not = cursor.execute('SELECT * FROM main_announcement A, main_enroll E WHERE E.user_id = %s'\
                                                ' AND A.cno_id = E.cno_id ORDER BY A.ann_date DESC LIMIT 5', [user_id])

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

    return render(request, 'main/course_detail.html', {'user_type': user_type, 'course': course, 'registered': registered,
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
