from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from django.views.generic import ListView, DetailView, View
from .models import Course, Lecture

class CourseListView(ListView):
    model = Course

class CourseDetailView(DetailView):
    model = Course

class LectureView(View):
    # model = Lecture

    def get(self, request, course_slug, lecture_slug, *args, **kwargs):
        course_queue = Course.objects.filter(slug=course_slug)
        if course_queue.exists():
            course = course_queue.first()

        lecture_q = Lecture.objects.filter(lecture_slug=lecture_slug)
        if lecture_q.exists():
            lecture = lecture_q.first()

        context = {
            'object': lecture
        }

        return render(request, 'main/lecture_detail.html', context)

# Create your views here.
def index(request):
    return HttpResponse("MAYACAT")

class Course_View(ListView):

    def course_detail(request, course_id):

        course = Course.objects.raw('SELECT * FROM courses_course WHERE course_id = %s', [course_id])

        # WILL BE CHANGED TO CURRENT USER ?
        user_id = request.user.id
        registered = Enroll.objects.raw('SELECT enroll_id FROM X WHERE user = %s AND cno = %s', [user_id], [course_id])

        lecture_count = Lecture.objects.filter(cno_id=course.cno).count()

        rating = Rate.objects.raw('SELECT AVG(score) FROM X WHERE cno = %s', [course_id])

        advertisement = Advertisement.objects.raw('SELECT advertisement FROM X WHERE cno = %s', [course_id])

        comments = Finishes.objects.raw('SELECT comment FROM X WHERE cno = %s', [course_id])

        return render(request, 'main/course_detail.html', {'course': course, 'registered': registered,
                                                           'lecture_count': lecture_count, 'rating': rating,
                                                           'advertisement': advertisement, 'comments': comments})


class Cart_View(ListView):
    def shopping_cart(request):

        # WILL BE CHANGED TO CURRENT USER ?
        user = request.user

        items = Inside_Cart.objects.raw('SELECT * FROM X WHERE username = %s', [user.name])

        return render(request, 'main/shopping_cart.html', {'items': items})
