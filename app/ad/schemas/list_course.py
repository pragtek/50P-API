import graphene
from ad.models import Course
from graphene_django import DjangoObjectType
from django.db.models import Q

class CourseType(DjangoObjectType):
    duration = graphene.Int()
    class Meta:
        model = Course
        fields = [
            'id',
            'course_id',
            'course_name',
            'teacher',
            'level'
        ]
        convert_choices_to_enum = False
    
    def resolve_duration(self,info):
        if self.duration:
            return self.duration.total_seconds()
        return None

class CourseDataModelType(graphene.ObjectType):
    rows = graphene.List(CourseType)
    total_rows = graphene.Int()
    
class Query(graphene.ObjectType):
    list_courses = graphene.Field(CourseDataModelType, search = graphene.String(), first = graphene.Int(), skip = graphene.Int())

    def resolve_list_courses(self, info, **kwargs):
        search = kwargs.get("search")
        first = kwargs.get("first")
        skip = kwargs.get("skip")

        filter = Q()

        if search:
            filter  = Q(course_name__icontains = search)
        
        list_courses = Course.objects.filter(filter)
        total_rows = list_courses.count()
        list_courses = list_courses.order_by("-created_date")

        if first:
            list_courses = list_courses[:first]

        if skip:
            list_courses = list_courses[skip:]
        
        return CourseDataModelType(
            rows = list_courses,
            total_rows = total_rows
        )
        
list_course_schema = graphene.Schema(query = Query)