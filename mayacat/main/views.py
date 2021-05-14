import sys

from django.shortcuts import render, redirect
from django.db import connection, DatabaseError, Error
from django.http import HttpResponse, HttpResponseRedirect
import uuid

from django.views.generic import ListView, View
from .models import *
from accounts.models import *
from courses.models import Course
from .forms import *
from datetime import datetime

cursor = connection.cursor()


def topic_course_listing_page(request, topicname):
    template_name = "main/topic_list_page.html"

    if request.method == 'GET':
        course_list = Course.objects.raw('select cno '
                                         'from courses_course '
                                         'inner join main_course_topic mct on courses_course.cno = mct.cno_id '
                                         'where topicname_id = %s;', [topicname])

        # obligatory user type check for base.html
        user_type = -1
        if request.user.is_authenticated:
            # check for user type
            cursor_ = connection.cursor()
            try:
                cursor_.execute('select type from accounts_defaultuser where user_ptr_id = %s;', [request.user.id])
                type_row = cursor_.fetchone()
                if type_row:
                    user_type = type_row[0]
            except DatabaseError:
                return HttpResponse("There was an error.<p> " + str(sys.exc_info()))
            finally:
                cursor_.close()

        topic_list = Topic.objects.raw('select * from main_topic;')

        return render(request, template_name, {'course_list': course_list, 'topic_list': topic_list,
                                               'user_type': user_type, 'topicname': topicname, })

    return HttpResponseRedirect('/')


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

        if user_type == -1:
            return HttpResponseRedirect('/login')

        topic_list = Topic.objects.raw('select * from main_topic order by topicname;')
        context = {
            'wishlist_q': wishlist_q,
            'user_type': user_type,
            'topic_list': topic_list,
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

        topic_list = Topic.objects.raw('select topicname from main_topic;')
        context = {
            'offers_q': offers_q,
            'user_type': user_type,
            'topic_list': topic_list,
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
        cursor = connection.cursor()
        cursor.execute('select type '
                       'from auth_user '
                       'inner join accounts_defaultuser ad on auth_user.id = ad.user_ptr_id '
                       'where id = %s;', [request.user.id])

        row = cursor.fetchone()
        user_type = -1
        if row:
            user_type = row[0]

        cursor.execute('SELECT topic_id FROM main_interested_in WHERE s_username_id = %s LIMIT 5', [request.user.id])
        interested_topics = cursor.fetchall()

        cursor.execute('SELECT count(*) FROM main_interested_in WHERE s_username_id = %s LIMIT 5', [request.user.id])
        interested_topics_count = cursor.fetchone()[0]

        topic_based_courses = [None] * interested_topics_count
        for i, topic in enumerate(interested_topics):
            cursor.execute('SELECT count(*) FROM main_course_topic CT, courses_course C '
                           'WHERE CT.topicname_id = %s AND C.cno = CT.cno_id LIMIT 5', [topic[0]])
            cnt = cursor.fetchone()[0]

            cursor.execute('SELECT slug, course_img, cname FROM main_course_topic CT, courses_course C '
                           'WHERE CT.topicname_id = %s AND C.cno = CT.cno_id LIMIT 5', [topic[0]])
            interested_courses = cursor.fetchall()

            topic_based_courses[i] = [None] * (cnt+1)

            topic_based_courses[i][0] = {
                "type": 0,
                "topic": topic[0],
                "cnt": cnt
            }
            for k in range(1, cnt+1):
                topic_based_courses[i][k] = {
                    "type": 1,
                    "slug": interested_courses[k-1][0],
                    "course_img": interested_courses[k-1][1],
                    "cname": interested_courses[k-1][2]
                }

        # TODO: THE COURSES WILL BE CHANGED AS TOP 5 MOST POPULAR AND TOP 5 HIGHEST RATED
        #  also the courses that are not private will be listed here
        cursor = connection.cursor()

        # THE COURSES WILL BE CHANGED AS TOP 5 MOST POPULAR AND TOP 5 HIGHEST RATED
        courses = Course.objects.raw('select * '
                                     'from courses_course;')

        topics = Topic.objects.raw('select * from main_topic order by topicname;')

        try:
            cursor.execute('select type '
                           'from auth_user '
                           'inner join accounts_defaultuser ad on auth_user.id = ad.user_ptr_id '
                           'where id = %s;', [request.user.id])
        except DatabaseError:
            return HttpResponse("There was an error.<p> " + str(sys.exc_info()))
        finally:
            cursor.close()

        return render(request, 'main/main.html', {'object_list': courses,
                                                  'topic_list': topics,
                                                  'user_type': user_type,
                                                  "topic_based": topic_based_courses})


def course_detail(request, course_slug):
    course_queue = Course.objects.raw('''SELECT * FROM courses_course WHERE slug = %s;''', [course_slug])

    # check whether the student is enrolled into this course
    # is course slug primary key

    if len(course_queue) > 0:
        course = course_queue[0]
        print("=2", course, course.cno)
    else:
        # 404 error
        print("error no course as the stated");

    cno = course.cno

    course = Course.objects.raw('SELECT * FROM courses_course WHERE course_id = %s', [course_id])

    user_id = request.user.id
    registered = Enroll.objects.raw('SELECT enroll_id FROM main_enroll WHERE user_id = %s AND cno_id = %s',
                                    [user_id, course_id])

    lecture_count = Lecture.objects.filter(cno_id=course.cno).count()
    ### TODO: RATE ARTIK YOK
    rating = Rate.objects.raw('SELECT AVG(score) FROM main_rate WHERE cno_id = %s', [course_id])
    advertisement = Advertisement.objects.raw('SELECT advertisement FROM main_advertisement WHERE cno_id = %s',
                                              [course_id])

    comments = Finishes.objects.raw('SELECT comment FROM main_finishes WHERE cno_id = %s', [course_id])

    cursor = connection.cursor()
    cursor.execute('select type '
                   'from auth_user '
                   'inner join accounts_defaultuser ad on auth_user.id = ad.user_ptr_id '
                   'where id = %s;', [request.user.id])

    row = cursor.fetchone()
    user_type = -1
    if row:
        user_type = row[0]

    topic_list = Topic.objects.raw('select * from main_topic;')

    return render(request, 'courses/course_detail.html',
                  {'user_type': user_type, 'course': course, 'registered': registered,
                   'lecture_count': lecture_count, 'rating': rating,
                   'advertisement': advertisement, 'comments': comments,
                   'topic_list': topic_list, })


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

        if user_type == 0:  # student
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
            cursor.execute(
                'SELECT ann_date, cname, ann_text FROM main_enroll as E, main_announcement A, courses_course C'
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

        elif user_type == 1:  # instructor
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
            cursor.execute(
                'SELECT ann_date, cname, ann_text FROM main_enroll as E, main_announcement A, courses_course C'
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
            notifications1 = []
            while gift_i < len(gift_arr) and ann_i < len(anns_arr):
                if anns_arr[ann_i][0] > gift_arr[gift_i][0]:
                    notifications1.append(anns_arr[ann_i])
                    ann_i = ann_i + 1
                else:
                    notifications1.append(gift_arr[gift_i])
                    gift_i = gift_i + 1

            if gift_i == len(gift_arr):
                while ann_i < len(anns_arr):
                    notifications1.append(anns_arr[ann_i])
                    ann_i = ann_i + 1
            elif ann_i == len(anns_arr):
                while gift_i < len(gift_arr):
                    notifications1.append(gift_arr[gift_i])
                    gift_i = gift_i + 1

            cursor = connection.cursor()
            cursor.execute(
                'SELECT date, cname, lecture_name, username FROM main_post P, courses_lecture L, courses_course C, auth_user U'
                ' WHERE P.lecture_no_id = L.lecture_no AND L.cno_id = C.cno AND owner_id = %s'
                ' AND P.username_id = U.id'
                , [request.user.id])
            temp_posts = cursor.fetchall()
            cursor.close()

            posts_arr = []
            for post in temp_posts:
                post = list(post)
                post.append("post")
                posts_arr.append(post)

            not1_i = 0
            post_i = 0
            notifications = []
            while not1_i < len(notifications1) and post_i < len(posts_arr):
                if posts_arr[post_i][0] > notifications1[not1_i][0]:
                    notifications.append(posts_arr[post_i])
                    post_i = post_i + 1
                else:
                    notifications.append(notifications1[not1_i])
                    not1_i = not1_i + 1

            if not1_i == len(notifications1):
                while post_i < len(posts_arr):
                    notifications.append(posts_arr[post_i])
                    post_i = post_i + 1
            elif post_i == len(posts_arr):
                while not1_i < len(notifications1):
                    notifications.append(notifications1[not1_i])
                    not1_i = not1_i + 1

        topic_list = Topic.objects.raw('select * from main_topic;')

        context = {'user_type': user_type, 'notifications': notifications, "topic_list": topic_list}
        return render(request, 'main/notifications.html', context)


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
            return HttpResponseRedirect('/login')

        cursor.execute('SELECT count(*) '
                       'FROM main_inside_cart '
                       'WHERE username_id = %s;', [request.user.id])
        count = cursor.fetchone()[0]

        cursor.execute('SELECT SUM(price) '
                       'FROM courses_course '
                       'inner join main_inside_cart AS mic ON courses_course.cno = mic.cno_id '
                       'WHERE mic.username_id = %s;', [request.user.id])
        total_price = cursor.fetchone()[0]

        cursor.execute(
            'SELECT inside_cart_id, cname, price, slug, course_img, receiver_username_id, inside_cart_id '
            'FROM courses_course AS cc, main_inside_cart AS mic '
            'WHERE cc.cno = mic.cno_id AND mic.username_id = %s;', [request.user.id])
        items_on_cart = cursor.fetchall()

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
                    'inside_cart_id': items_on_cart[i][6],
                    'receiver_username': receivers[i]
                }
        else:
            items = None
            count = 0
            total_price = 0

        topic_list = Topic.objects.raw('select * from main_topic;')

        return render(request, 'main/shopping_cart.html', {'user_type': user_type, 'items': items, 'path': request.path,
                                                           'count': count, 'total_price': total_price,
                                                           'user_id': request.user.id,
                                                           'topic_list': topic_list, })

    def post(self, request):
        cursor = connection.cursor()

        pull = GiftForm(request.POST)
        if pull.is_valid():
            receiver_username = pull.cleaned_data['receiver_id']
            item_id = pull.cleaned_data['item_id']
            item_id = int(item_id)

            cursor.execute('SELECT id, username, is_superuser'
                           ' FROM auth_user WHERE username = %s', [receiver_username])
            receiver_id = cursor.fetchall()

            if len(receiver_id) == 0:
                return HttpResponseRedirect(request.path)

            if receiver_id[0][0] == request.user.id:
                return HttpResponseRedirect(request.path)

            if receiver_id[0][2] == 1:
                return HttpResponseRedirect(request.path)

            if receiver_id[0][0]:
                cursor.execute('UPDATE main_inside_cart '
                               'SET receiver_username_id = %s '
                               'WHERE inside_cart_id = %s', [receiver_id[0][0], item_id])
        return HttpResponseRedirect(request.path)


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

        topic_list = Topic.objects.raw('select * from main_topic order by topicname;')

        return render(request, 'main/checkout.html', {'user_type': user_type, 'topic_list': topic_list, })

    def post(self, request):
        cursor = connection.cursor()

        cursor.execute('SELECT slug, receiver_username_id, cno '
                       'FROM courses_course '
                       'inner join main_inside_cart AS mic ON courses_course.cno = mic.cno_id '
                       'WHERE mic.username_id = %s;', [request.user.id])

        items_on_cart = cursor.fetchall()

        if (len(items_on_cart) > 0):
            items = [None] * len(items_on_cart)
            for i in range(0, len(items_on_cart)):
                items[i] = {
                    'slug': items_on_cart[i][0],
                    'isGift': items_on_cart[i][1],
                    'cno': items_on_cart[i][2],
                }
        else:
            items = None

        for item in items:
            receiver = item.get('isGift')
            if receiver !=  None:
                add_to_my_courses(request, item)

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

        topic_list = Topic.objects.raw('select * from main_topic;')

        context = {'items': items, 'user_type': user_type, "topic_list": topic_list}
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


class TaughtCoursesView(View):
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

        cursor.execute('SELECT cname, slug FROM courses_course WHERE owner_id = %s',
                       [request.user.id])
        owned_courses = cursor.fetchall()

        cursor.execute(
            'SELECT cname, slug FROM courses_course C, main_teaches T, courses_lecture L WHERE T.user_id = %s'
            ' AND T.lecture_no_id = L.lecture_no AND L.cno_id = C.cno AND cno NOT IN'
            ' (SELECT cno FROM courses_course WHERE owner_id = %s)', [request.user.id, request.user.id])
        taught_courses = cursor.fetchall()

        topic_list = Topic.objects.raw('select * from main_topic;')

        context = {'user_type': user_type, 'owned_courses': owned_courses, 'taught_courses': taught_courses,
                   "topic_list": topic_list}
        return render(request, 'main/taught_courses.html', context)


def add_to_my_courses(request, item):
    cursor = connection.cursor()
    course_slug = item.get('slug')
    receiver_id = item.get('isGift')

    course = Course.objects.raw('SELECT * FROM courses_course WHERE slug = "' + course_slug + '" LIMIT 1')[0]
    cno = course.cno

    user_id = request.user.id

    if receiver_id == user_id:

        my_courses = Enroll.objects.raw('SELECT * '
                                        'FROM main_enroll '
                                        'WHERE user_id = %s AND cno_id = %s;',
                                        [user_id, cno])
    else:

        my_courses = Enroll.objects.raw('SELECT * '
                                        'FROM main_enroll '
                                        'WHERE user_id = %s AND cno_id = %s;',
                                        [receiver_id, cno])


    if len(list(my_courses)) == 0:
        if receiver_id == user_id:
            cursor.execute('INSERT INTO main_enroll (cno_id, user_id) VALUES (%s, %s);',
                       [cno, user_id])
        else:
            cursor.execute('INSERT INTO main_enroll (cno_id, user_id) VALUES (%s, %s);',
                           [cno, receiver_id])

            today = datetime.today().strftime('%Y-%m-%d')

            cursor.execute('INSERT INTO main_gift (date, course_id, receiver_id, sender_id) '
                           'VALUES (%s, %s, %s, %s);',[today, cno, receiver_id, user_id])

        cursor.execute('''DELETE FROM main_inside_cart 
                            WHERE username_id = %s ''', [request.user.id])

    cursor.close()


class TrashView(View):

    def post(self, request, inside_cart_id):
        cursor = connection.cursor()

        course = Inside_Cart.objects.raw(
            'SELECT * FROM main_inside_cart WHERE inside_cart_id = "' + inside_cart_id + '" LIMIT 1')[0]
        ici = course.inside_cart_id

        # course = Course.objects.raw('SELECT * FROM courses_course WHERE slug = "' + course_slug + '" LIMIT 1')[0]
        # cno = course.cno

        cursor.execute('DELETE '
                       'FROM main_inside_cart '
                       'WHERE inside_cart_id = %s AND username_id = %s', [ici, request.user.id])
        cursor.close()

        return HttpResponseRedirect('/cart')


class DiscountsView(View):
    template_name = "main/discounts.html"

    def get(self, request):
        try:
            current_discounts = Offered_Discount.objects.raw('select * '
                                                             'from adminpanel_offered_discount '
                                                             'where curdate() between start_date and end_date;')
        except Error:
            return HttpResponse("There was an error.<p> " + str(sys.exc_info()))

        user_type = get_user_type(request)

        topic_list = Topic.objects.raw('select * from main_topic;')
        return render(request, self.template_name, {'topic_list': topic_list,
                                                    'current_discounts': current_discounts,
                                                    'user_type': user_type, })


class JoinCoursesView(View):
    template_name = "main/discount_course.html"

    def get(self, request, offer_no):
        if request.user.is_authenticated:
            # check if the user is an instructor, list the instructor's courses, and create multiple selection boxes
            cursor = connection.cursor()
            try:
                cursor.execute('select type from accounts_defaultuser where user_ptr_id = %s;', [request.user.id])
                user_type = cursor.fetchone()
                if user_type:  # the user ought to be recorded inside defaultuser as well, but just in case
                    user_type = user_type[0]
            except Error:
                return HttpResponse("There was an error.<p> " + str(sys.exc_info()))
            finally:
                cursor.close()

            if user_type != 1:  # not an instructor
                return HttpResponseRedirect('/')  # return to main page

            topic_list = Topic.objects.raw('select * from main_topic;')

            courses_from_instructor = CoursesDiscount(instructor_id=request.user.id)
            return render(request, self.template_name, {'user_type': user_type, 'topic_list': topic_list,
                                                        'courses_from_instructor': courses_from_instructor, })

    def post(self, request, offer_no):
        # add offer to the new discount table
        if request.user.is_authenticated:
            courses_from_instructor = CoursesDiscount(request.POST, instructor_id=request.user.id)

            if courses_from_instructor.is_valid():
                courses = courses_from_instructor.cleaned_data.get('courses')

                for course in courses:
                    cursor = connection.cursor()
                    try:
                        cursor.execute('insert into main_discount (cno_id, offerno_id) values (%s, %s);',
                                       [course.cno, offer_no])
                    except Error:
                        return HttpResponse('Error.')
                    finally:
                        cursor.close()
        return redirect('main:discounts')


def get_user_type(request):
    if request.user.is_authenticated:
        cursor = connection.cursor()
        try:
            cursor.execute('select type from accounts_defaultuser where user_ptr_id = %s;', [request.user.id])
            user_type = cursor.fetchone()
            if user_type:
                user_type = user_type[0]
        except Error:
            HttpResponse("There was an error.<p> " + str(sys.exc_info()))
        finally:
            cursor.close()

        return user_type
    return -1
