from django.shortcuts import render, redirect
from django.db import connection
from django.http import HttpResponse, HttpResponseRedirect
import uuid

from django.views.generic import ListView, DetailView, View
from .models import *
from accounts.models import *

cursor = connection.cursor()


class MainView(View):
    def get(self, request):
        # THE COURSES WILL BE CHANGED AS TOP 5 MOST POPULAR AND TOP 5 HIGHEST RATED
        courses = Course.objects.raw('select * '
                                     'from courses_course;')

        topics = Topic.objects.raw('select * from main_topic order by topicname;')

        return render(request, 'main/main.html', {'object_list': courses,
                                                  'topic_list':topics})


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

        # log in before like anything
        if user_type == -1:
            return HttpResponseRedirect('/login')

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
    # WILL BE CHANGED TO CURRENT USER ?
    user_id = request.user.id
    registered = Enroll.objects.raw('SELECT enroll_id FROM main_enroll WHERE user_id = %s AND cno_id = %s', [user_id], [course_id])

    lecture_count = Lecture.objects.filter(cno_id=course.cno).count()

    rating = Rate.objects.raw('SELECT AVG(score) FROM main_rate WHERE cno_id = %s', [course_id])
    advertisement = Advertisement.objects.raw('SELECT advertisement FROM main_advertisement WHERE cno_id = %s', [course_id])

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

    return render(request, 'courses/course_detail.html', {'user_type': user_type, 'course': course, 'registered': registered,
                                                       'lecture_count': lecture_count, 'rating': rating,
                                                       'advertisement': advertisement, 'comments': comments})


class ShoppingCartView(View):

    def get(self, request, course_slug = None):

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

        # The function is called from (add to cart) button
        if(course_slug is not None):

            course = Course.objects.raw('SELECT * FROM courses_course WHERE slug = "' + course_slug + '" LIMIT 1')[0]
            cno = course.cno


            my_courses = Enroll.objects.raw('SELECT * '
                                            'FROM main_enroll '
                                            'WHERE user_id = %s AND cno_id = %s;', [request.user.id, cno])

            my_cart = Inside_Cart.objects.raw('SELECT * '
                                              'FROM main_inside_cart '
                                              'WHERE username_id = %s AND cno_id = %s;', [request.user.id, cno])

            cursor.execute('INSERT INTO main_inside_cart (cno_id, username_id) VALUES (%s, %s);',
                           [cno, request.user.id])

            '''
            if not (len(list(my_courses)) == 0 or len(list(my_cart)) == 0):
                cursor.execute('INSERT INTO main_gift ( course_id, sender_id) VALUES (%s, %s);',
                               [cno, request.user.id])

                cursor.execute('UPDATE main_inside_cart '
                                'SET receviver_username_id = 1 '
                                'WHERE cno_id = %s AND username_id = %s);', [cno, request.user.id])
            
            '''

        user = request.user

        cursor.execute('SELECT count(*) '
                       'FROM main_inside_cart '
                       'WHERE username_id = %s;', [request.user.id])
        count = cursor.fetchone()[0]


        cursor.execute('SELECT SUM(price) '
                       'FROM courses_course '
                       'inner join main_inside_cart AS mic ON courses_course.cno = mic.cno_id '
                       'WHERE mic.username_id = %s;', [request.user.id])
        total_price = cursor.fetchone()[0]


        cursor.execute('SELECT cno, cname, price, slug, situation, is_private, course_img, description, owner_id, receiver_username_id, inside_cart_id '
                       'FROM courses_course AS cc, main_inside_cart AS mic '
                       'WHERE cc.cno = mic.cno_id AND mic.username_id = %s;', [request.user.id])
        items_on_cart = cursor.fetchall()

        if(len(items_on_cart) > 0):
            items = [None] * len(items_on_cart)
            for i in range(0, len(items_on_cart)):
                items[i] = {
                    'cno': items_on_cart[i][0],
                    'cname': items_on_cart[i][1],
                    'price': items_on_cart[i][2],
                    'slug': items_on_cart[i][3],
                    'course_img': items_on_cart[i][6],
                    'owner_id': items_on_cart[i][8],
                    'inside_cart_id': items_on_cart[i][10],
                    #'isGift': items_on_cart[i][9],
                }
        else:
            items = None
            count = 0
            total_price = 0


        return render(request, 'main/shopping_cart.html', {'user_type': user_type, 'items': items,
                                                           'count': count, 'total_price': total_price})

    def post(self, request, course_slug):
        cursor = connection.cursor()

        pull = Gift(request.POST)

        if pull.is_valid():

            receiver_id = pull.cleaned_data['receiver_id']

            course = Course.objects.raw('SELECT * FROM courses_course WHERE slug = "' + course_slug + '" LIMIT 1')[0]
            cno = course.cno

            if(receiver_id):
                cursor.execute('UPDATE main_gift '
                               'SET receviver_id = %s '
                               'WHERE course_id = %s AND sender_id = %s',[receiver_id, cno, request.user.id])


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
                    #'isGift': items_on_cart[i][1],
                }
        else:
            items = None

        for item in items:
            add_to_my_courses(request, item)

        cursor.execute('DELETE FROM main_inside_cart WHERE username_id = %s', [request.user.id])

        return HttpResponseRedirect('/cart')


def add_to_my_courses(request, item):

    cursor = connection.cursor()
    course_slug = item.get('slug')
    #isGift = item.get('isGift')

    course = Course.objects.raw('SELECT * FROM courses_course WHERE slug = "' + course_slug + '" LIMIT 1')[0]
    cno = course.cno

    user_id = request.user.id

    my_courses = Enroll.objects.raw('SELECT * '
                                    'FROM main_enroll '
                                    'WHERE user_id = %s AND cno_id = %s;',
                                    [user_id, cno])
    '''
    
    if isGift != 0:
        cursor.execute('INSERT INTO main_enroll (cno_id, user_id) VALUES (%s, %s);',
                       [isGift, user_id])
    '''

    if len(list(my_courses)) == 0:
        cursor.execute('INSERT INTO main_enroll (cno_id, user_id) VALUES (%s, %s);',
                       [cno, user_id])

    cursor.close()

class TrashView(View):

    def post(self, request, course_slug, inside_cart_id):

        cursor = connection.cursor()

        course = Inside_Cart.objects.raw('SELECT * FROM main_inside_cart WHERE inside_cart_id = "' + inside_cart_id + '" LIMIT 1')[0]
        ici = course.inside_cart_id

        #course = Course.objects.raw('SELECT * FROM courses_course WHERE slug = "' + course_slug + '" LIMIT 1')[0]
        #cno = course.cno

        cursor.execute('DELETE '
                       'FROM main_inside_cart '
                       'WHERE inside_cart_id = %s AND username_id = %s', [ici, request.user.id])
        cursor.close()

        return HttpResponseRedirect('/cart')

