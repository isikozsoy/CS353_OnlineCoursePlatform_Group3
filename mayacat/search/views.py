from django.db import connection
from django.db.models.expressions import RawSQL
from django.shortcuts import render
from django.views.generic import View, ListView

from courses.models import Course


def search_amongst_courses(pattern):
    course_qset = Course.objects.raw("select * from courses_course")

    M = len(pattern)
    lps = [0] * M
    j = 0  # index for pattern

    # search algorithm for course names is given below
    for course in course_qset:
        course_name = course.cname
        N = len(course_name)

        i = 0  # index for course name
        while i < N:
            if pattern[j] == course_name[i]:
                i += 1;
                j += 1
            if j == M:
                j = lps[j - 1]

            # a mismatch
            elif i < N and pattern[j] != course_name[i]:
                if j != 0:
                    j = lps[j - 1]
                else:
                    i += 1


class SearchView(View):
    template_name = "search.html"
    model = Course

    def get(self, request):
        q = self.request.GET.get('q')
        q = '%' + q + '%'

        object_list = Course.objects.raw(
            "select * " +
            "from courses_course " +
            "where cname like %s;", [q]
        )
        if request.user.is_authenticated:
            cursor = connection.cursor()
            try:
                cursor.execute('select type from accounts_defaultuser where user_ptr_id = %s;', [request.user.id])
                user_type = cursor.fetchone()[0]
            finally:
                cursor.close()

        return render(request=request, template_name=self.template_name, context={'object_list': object_list,
                                                                                  'user_type': user_type})
