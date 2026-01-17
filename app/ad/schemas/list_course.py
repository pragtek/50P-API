import graphene
from graphene_django import DjangoObjectType
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from datetime import timedelta
from graphql import GraphQLError
from ad.models import Course, Teacher
from authtf.models.user import User
from ad.schemas.course_chapter import CourseChapterType
import datetime



class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "phone")

class CourseType(DjangoObjectType):
    duration = graphene.Float()
    chapters = graphene.List(CourseChapterType)

    class Meta:
        model = Course
        fields = [
            'id',
            'course_id',
            'course_name',
            'teacher',
            'level',
            'applicants',
            'chapters'
            
        ]
        convert_choices_to_enum = False

    def resolve_chapters(self, info):
        return self.chapters.filter(is_deleted=False)
    
    def resolve_duration(self, info):
        if self.duration:
            return self.duration.total_seconds()
        return None

class CourseDataModelType(graphene.ObjectType):
    rows = graphene.List(CourseType)
    total_rows = graphene.Int()



class Query(graphene.ObjectType):
    all_course_list = graphene.Field(
        CourseDataModelType, 
        search=graphene.String(), 
        first=graphene.Int(), 
        skip=graphene.Int()
    )
    
    list_course_by_id = graphene.Field(
        CourseType, 
        course_id=graphene.Int(required=True)
    )
    
    all_courses_by_user = graphene.Field(
        CourseDataModelType,
        user_id=graphene.Int(required=True), 
        search=graphene.String(),
        first=graphene.Int(), 
        skip=graphene.Int()
    )
    
    def resolve_all_course_list(self, info, **kwargs):
        search = kwargs.get("search")
        first = kwargs.get("first")
        skip = kwargs.get("skip")

        qs = Course.objects.all().order_by("-id") 

        if search:
            qs = qs.filter(Q(course_name__icontains=search) | Q(level__icontains=search))
        
        total_rows = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]
        
        return CourseDataModelType(rows=qs, total_rows=total_rows)

    def resolve_list_course_by_id(self, info, course_id):
        try:
            return Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return None
    
    def resolve_all_courses_by_user(self, info, user_id, **kwargs):
        search = kwargs.get("search")
        first = kwargs.get("first")
        skip = kwargs.get("skip")

        try:
            user = User.objects.get(pk=user_id)
            qs = user.enrolled_courses.all().order_by("-id")

            if search:
                qs = qs.filter(
                    Q(course_name__icontains=search) |
                    Q(level__icontains=search) 
                )
            
            total_count = qs.count()

            if skip: qs = qs[skip:]
            if first: qs = qs[:first]

            return CourseDataModelType(total_rows=total_count, rows=qs)
        
        except User.DoesNotExist:
            return CourseDataModelType(total_rows=0, rows=[])
        except Exception as e:
            raise GraphQLError(f"An error occurred: {str(e)}")
        
   

class ApplyCourse(graphene.Mutation):
    class Arguments:
        course_id = graphene.Int(required=True)
        user_id = graphene.Int(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, course_id, user_id):
        try:
            user = User.objects.get(pk=user_id)
            course = Course.objects.get(pk=course_id)
            
            if course.applicants.filter(pk=user.pk).exists():
                return ApplyCourse(success=False, message="Already enrolled.")
            
            course.applicants.add(user)
            return ApplyCourse(success=True, message="Enrollment successful.")
        except Exception as e:
            raise GraphQLError(str(e))


class CreateCourse(graphene.Mutation):
    class Arguments:
        course_name = graphene.String(required=True)
        level = graphene.String(required=True)
        teacher_id = graphene.Int(required = True)
        duration = graphene.Int(required=True)

    course = graphene.Field(CourseType)
    
    def mutate(self, info, course_name, level, teacher_id, duration=30):
        teacher_instance = None
        try:
            teacher_instance = Teacher.objects.get(pk=teacher_id)
        except ObjectDoesNotExist:
            raise Exception(f"Error: A teacher with the ID {teacher_id} was not found.")
        
        duration_obj = datetime.timedelta(days=duration)
        new_course = Course.objects.create(
            course_name = course_name,
            level = level,
            teacher = teacher_instance,
            duration = duration_obj
        )
        return CreateCourse(course = new_course)

class UpdateCourse(graphene.Mutation):
    class Arguments:
        course_id = graphene.Int()
        course_name = graphene.String()
        level = graphene.String()
        teacher_id = graphene.UUID()
        duration = graphene.Int()
    
    course = graphene.Field(CourseType)


    def mutate(self, info, course_id, **kwargs):
        try:
            course_instance = Course.objects.get(pk=course_id)
        except:
            raise Exception("Course not found with the provided ID.")
        
        course_instance.course_name = kwargs.get("course_name")
        course_instance.level = kwargs.get("level")
        course_instance.duration = datetime.timedelta(days = kwargs.get("duration"))
        teacher_id = kwargs.get("teacher_id")
        if teacher_id is not None:
            try:
                teacher_instance = Teacher.objects.get(unique_id = teacher_id) 
                course_instance.teacher = teacher_instance
            except ObjectDoesNotExist:
                raise Exception(f"Teacher with ID {teacher_id} not found.")
            
        course_instance.save(
            update_fields=[
                "course_name",
                "teacher",
                "level",
                "duration"

            ]
        )
        return UpdateCourse(course=course_instance)

class DeleteCourse(graphene.Mutation):
    class Arguments:
        id = graphene.Int()
    
    ok = graphene.Boolean()

    def mutate(self, info, id):
        try:
            item = Course.objects.get(pk = id)
        
        except Course.DoesNotExist:
            raise Exception(f"Course the ID {id} does not exist.")
        
        item.is_deleted = True
        item.save(update_fields = ["is_deleted"])
        return DeleteCourse(ok = True)

    
class Mutation(graphene.ObjectType):
    apply_course = ApplyCourse.Field()
    add_course = CreateCourse.Field()
    update_course = UpdateCourse.Field()
    delete_course = DeleteCourse.Field()

        
list_course_schema = graphene.Schema(query=Query, mutation=Mutation)