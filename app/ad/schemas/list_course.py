import graphene
from graphene_django import DjangoObjectType
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from datetime import timedelta
from graphql import GraphQLError
from ad.models import Course, Teacher
from authtf.models.user import User


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

        qs = Course.objects.all().order_by("-id") # Update ordering field if needed

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

class Mutation(graphene.ObjectType):
    apply_course = ApplyCourse.Field()
        
list_course_schema = graphene.Schema(query=Query, mutation=Mutation)