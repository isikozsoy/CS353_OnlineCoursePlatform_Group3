from django.db import connection, DatabaseError
from django.db.models.expressions import RawSQL
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View, ListView

from courses.models import Course
from main.models import Topic


class SearchView(View):
    template_name = "search.html"
    model = Course

    def get(self, request):
        q = self.request.GET.get('q')
        q = '%' + q + '%'

        object_list = Course.objects.raw(
            "select * " +
            "from courses_course " +
            "where cname like %s and is_private != 1;", [q]
        )
        print("select * " +
            "from courses_course " +
            "where cname like %s and is_private != 1;", [q])
        user_type = -1
        if request.user.is_authenticated:
            cursor = connection.cursor()
            try:
                cursor.execute('select user_type from auth_user where id = %s;', [request.user.id])
                user_type = cursor.fetchone()[0]
            finally:
                cursor.close()

        topic_list = Topic.objects.raw('select * from main_topic order by topicname;')

        return render(request=request, template_name=self.template_name, context={'object_list': object_list,
                                                                                  'user_type': user_type,
                                                                                  'topic_list': topic_list, })
