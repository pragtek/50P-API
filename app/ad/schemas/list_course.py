import graphene
from ad.models import Course
from graphene_django import DjangoObjectType
from django.db.models import Q
from authtf.models.user import User
from django.core.exceptions import ObjectDoesNotExist
from ad.models import Teacher
from datetime import timedelta

class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "phone")

class CourseType(DjangoObjectType):
    duration = graphene.Float()
    class Meta:
        model = Course
        fields = [
            'id',
            'course_id',
            'course_name',
            'teacher',
            'level',
            'user'
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

        if skip is not None and first is not None:
            list_courses = list_courses[skip : skip + first]

        elif first:
            list_courses = list_courses[:first]

        elif skip:
            list_courses = list_courses[skip:]
        
        return CourseDataModelType(
            rows = list_courses,
            total_rows = total_rows
        )
class CreateCourse(graphene.Mutation):
    class Arguments:
        course_name = graphene.String(required = True)
        teacher_id = graphene.Int(required = True)
        level = graphene.String(required = True)
        duration = graphene.Int(required = True)
        user_id = graphene.Int(required = True)
    
    course = graphene.Field(CourseType)

    def mutate(self, info,  user_id, teacher_id, **kwargs):
        user_instance = None
        try:
            user_instance = User.objects.get(pk = user_id)
        except ObjectDoesNotExist:
            raise Exception(f"User with {user_id} was not found.")
        
        teacher_instance = None
        try:
            teacher_instance = Teacher.objects.get(pk = teacher_id)
        except ObjectDoesNotExist:
            raise Exception(f"Teacher with id {teacher_id} does not exist.")
        new_course = Course.objects.create(
            course_name = kwargs.get("course_name"),
            level = kwargs.get("level"),
            duration = timedelta(seconds = kwargs.get("duration")),
            teacher = teacher_instance,
            user = user_instance
        )
        return CreateCourse(course = new_course)

class Mutation(graphene.ObjectType):
    add_courses = CreateCourse.Field()
        
list_course_schema = graphene.Schema(query = Query, mutation = Mutation)