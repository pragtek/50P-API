import graphene
from django.db import models
from graphene_django import DjangoObjectType
from ad.models import Course
from ad.models.teachers import Teacher
from django.core.exceptions import ValidationError
from django.db.models import Q
from graphql_jwt.decorators import login_required


class CourseType(DjangoObjectType):
    class Meta:
        model = Course
        fields = (
            "id",
            "course_id",
            "course_name",
            "duration",
            "teacher",
            "level"
        )

class CourseDataModelType(graphene.ObjectType):
    total_rows = graphene.Int()
    rows = graphene.List(CourseType)

class Query(graphene.ObjectType):
    course_by_id = graphene.Field(
                    CourseType,
                    id = graphene.Int()
                    )
    
    all_courses = graphene.Field(
        CourseDataModelType,
        first = graphene.Int(),
        search = graphene.String(),
        skip = graphene.Int()
        )
    
    def resolve_course_by_id(self, info, id):
        return Course.objects.all(pk=id)
    
    def resolve_all_courses(self, info, **kwargs):
        first = kwargs.get("first")
        search = kwargs.get("search")
        skip = kwargs.get("skip")

        filter = Q()

        if search:
            filter = Q(course_name__icontains = search)
        
        all_courses = Course.objects.filter(filter)
        all_courses = all_courses.order_by("-created_date")
        totalCount = all_courses.count()

        if first:
            all_courses = all_courses[:first]
        
        if skip:
            all_courses = all_courses[skip:]
        
        return CourseDataModelType(
            total_rows = totalCount,
            rows = all_courses
        )

class CreateCourse(graphene.Mutation):
    class Arguments:
        course_name = graphene.String(required=True)
        level = graphene.String(required=True)
        teacher_id = graphene.UUID(required = True)
        duration = graphene.Int(required=True)

    course = graphene.Field(CourseType)
    
    @login_required
    def mutate(self, info, course_name, level, teacher_id, duration=30):
        teacher_instance = None
        try:
            teacher_instance = Teacher.objects.get(unique_id=teacher_id)
        except Teacher.DoesNotExist:
            raise ValidationError(f"Error: A teacher with the ID {teacher_id} was not found.")
        
        session_user = info.context.user
        duration_obj = datetime.timedelta(days=duration)
        new_course = Course.objects.create(
            course_name = course_name,
            level = level,
            teacher = teacher_instance,
            duration = duration_obj,
            user = session_user
        )
        return CreateCourse(course = new_course)

class UpdateCourse(graphene.Mutation):
    class Arguments:
        course_id = graphene.Int()
        course_name = graphene.String(required=True)
        level = graphene.String(required=True)
        teacher_id = graphene.UUID(required = True)
        duration = graphene.Int(required=True)
    
    course = graphene.Field(CourseType)

    @login_required
    def mutate(self, info, course_id, **kwargs):
        try:
            course_instance = Course.objects.get(course_id=id, user = info.context.user)
        except:
            raise ValidationError("Course not found with the provided ID.")
        
        course_instance.course_name = kwargs.get("course_name")
        course_instance.level = kwargs.get("level")
        teacher_id = kwargs.get("teacher_id")
        if teacher_id is not None:
            try:
                teacher_instance = Teacher.objects.get(unique_id = teacher_id) 
                course_instance.teacher = teacher_instance
            except Teacher.DoesNotExist:
                raise ValidationError(f"Teacher with ID {teacher_id} not found.")
            
        course_instance.save()






class Mutation(graphene.ObjectType):
    add_course = CreateCourse.Field()
    update_course = UpdateCourse.Field()
    
courses_schema = graphene.Schema(query = Query, mutation = Mutation)