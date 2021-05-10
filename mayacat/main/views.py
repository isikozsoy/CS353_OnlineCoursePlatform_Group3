from django.shortcuts import render, redirect
from django.db import connection
from django.http import HttpResponse, HttpResponseRedirect
import uuid

from django.views.generic import ListView, DetailView, View
from .models import *
from accounts.models import *
from .forms import *
from datetime import datetime

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


class ShoppingCartView(View):

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

        # log in before buy anything
        if user_type == -1:
            return HttpResponseRedirect('/')
        '''
        cursor.execute('SELECT count(*) '
                       'FROM main_inside_cart '
                       'WHERE username_id = %s;', [request.user.id])
        count = cursor.fetchone()[0]
        '''
        cursor.execute('SELECT SUM(price) '
                       'FROM courses_course '
                       'inner join main_inside_cart AS mic ON courses_course.cno = mic.cno_id '
                       'WHERE mic.username_id = %s;', [request.user.id])
        total_price = cursor.fetchone()[0]

        cursor.execute(
            'SELECT inside_cart_id, cname, price, slug, course_img, receiver_username_id '
            'FROM courses_course AS cc, main_inside_cart AS mic '
            'WHERE cc.cno = mic.cno_id AND mic.username_id = %s;', [request.user.id])
        items_on_cart = cursor.fetchall()
        count = len(items_on_cart)

        cursor.execute('SELECT username FROM main_inside_cart LEFT JOIN auth_user'
                       ' on receiver_username_id = id'
                       ' WHERE username_id = %s', [request.user.id])
        receivers = cursor.fetchall()

        if count > 0:
            items = [None] * count
            for i in range(0, count):
                items[i] = {
                    'item_id': items_on_cart[i][0],
                    'cname': items_on_cart[i][1],
                    'price': items_on_cart[i][2],
                    'slug': items_on_cart[i][3],
                    'course_img': items_on_cart[i][4],
                    'isGift': items_on_cart[i][5],
                    'receiver_username': receivers[i]
                }
        else:
            items = None
            count = 0
            total_price = 0

        return render(request, 'main/shopping_cart.html', {'user_type': user_type, 'items': items, 'path': request.path,
                                                           'count': count, 'total_price': total_price,
                                                           'user_id': request.user.id})


    def post(self, request):
        cursor = connection.cursor()

        pull = GiftForm(request.POST)
        if pull.is_valid():
            receiver_username = pull.cleaned_data['receiver_id']
            item_id = pull.cleaned_data['item_id']
            item_id = int(item_id)

            cursor.execute('SELECT id FROM auth_user WHERE username = %s', [receiver_username])
            receiver_id = cursor.fetchone()[0]

            if receiver_id:
                cursor.execute('UPDATE main_inside_cart '
                               'SET receiver_username_id = %s '
                               'WHERE inside_cart_id = %s', [receiver_id, item_id])
        return HttpResponseRedirect(request.path)


def remove_from_cart(request, item_id):
    print("-------------inside remove")
    item_id = int(item_id)
    cursor = connection.cursor()
    cursor.execute('DELETE FROM main_inside_cart '
                   'WHERE inside_cart_id = %s', [item_id])
    cursor.close()
    return redirect("main:cart")


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

    def post(self, request):
        cursor = connection.cursor()

        cursor.execute('SELECT slug, receiver_username_id '
                       'FROM courses_course '
                       'inner join main_inside_cart AS mic ON courses_course.cno = mic.cno_id '
                       'WHERE mic.username_id = %s;', [request.user.id])

        items_on_cart = cursor.fetchall()

        if (len(items_on_cart) > 0):
            items = [None] * len(items_on_cart)
            for i in range(0, len(items_on_cart)):
                items[i] = {
                    'slug': items_on_cart[i][0],
                    # 'isGift': items_on_cart[i][1],
                }
        else:
            items = None

        for item in items:
            add_to_my_courses(request, item)

        cursor.execute('DELETE FROM main_inside_cart WHERE username_id = %s', [request.user.id])

        return HttpResponseRedirect('/cart')

class AdOffersView(View):
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

        # Only one ad for the same date. Mark as refused.
        cursor.execute('SELECT a1.advertisementno FROM main_advertisement AS a1, main_advertisement AS a2, '
                       'courses_course WHERE owner_id = %s AND a1.startdate <= a2.finishdate AND '
                       'a1.finishdate >= a2.startdate AND a1.status = %s AND a2.status = %s',
                       [request.user.id, 0, 2])
        ad_to_refuse = cursor.fetchall()
        for ad in ad_to_refuse:
            cursor.execute('UPDATE main_advertisement '
                           'SET status = 1 '
                           'WHERE advertisementno = %s', [ad])

        # Date is passed. Mark as refused.
        today = datetime.today().strftime('%Y-%m-%d')
        cursor.execute('SELECT advertisementno FROM main_advertisement INNER JOIN courses_course on cno_id = cno '
                       'WHERE owner_id = %s AND startdate <= %s', [request.user.id, today])
        ad_passed = cursor.fetchall()
        for ad_no in ad_passed:
            cursor.execute('UPDATE main_advertisement '
                           'SET status = 1 '
                           'WHERE advertisementno = %s', [ad_no])

        cursor.execute('SELECT advertisementno, advertisement, status, payment, startdate, finishdate, cname'
                       ' FROM main_advertisement INNER JOIN courses_course on cno_id = cno'
                       ' WHERE owner_id = %s', [request.user.id])
        offers = cursor.fetchall()

        cursor.execute('SELECT username FROM main_advertisement INNER JOIN auth_user on id = ad_username_id'
                       ' WHERE cno_id in (SELECT cno FROM courses_course WHERE owner_id = %s)', [request.user.id])
        advertiser_usernames = cursor.fetchall()

        if len(offers) > 0:
            items = [None] * len(offers)
            for i in range(0, len(offers)):
                items[i] = {
                    'ad_no': offers[i][0],
                    'ad': offers[i][1],
                    'status': offers[i][2],
                    'payment': offers[i][3],
                    'startdate': offers[i][4],
                    'finishdate': offers[i][5],
                    'cname': offers[i][6],
                    'ad_username': advertiser_usernames[i]
                }

        context = {'items': items, 'user_type': user_type}
        return render(request, 'main/ad_offers.html', context)

def accept_ad(request, ad_no):
    cursor = connection.cursor()
    cursor.execute('UPDATE main_advertisement '
                   'SET status = 2 '
                   'WHERE advertisementno = %s', [ad_no])

    cursor.execute('SELECT a1.advertisementno FROM main_advertisement AS a1, main_advertisement AS a2, '
                   'courses_course WHERE owner_id = %s AND a1.startdate <= a2.finishdate AND '
                   'a1.finishdate >= a2.startdate AND a1.status = %s AND a2.status = %s',
                   [request.user.id, 0, 2])
    ad_to_refuse = cursor.fetchall()
    for ad in ad_to_refuse:
        cursor.execute('UPDATE main_advertisement '
                       'SET status = 1 '
                       'WHERE advertisementno = %s', [ad])
    return redirect('main:ad_offers')

def refuse_ad(request, ad_no):
    cursor = connection.cursor()
    cursor.execute('UPDATE main_advertisement '
                   'SET status = 1 '
                   'WHERE advertisementno = %s', [ad_no])
    return redirect('main:ad_offers')