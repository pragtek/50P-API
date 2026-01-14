import graphene
from graphene_django import DjangoObjectType
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from datetime import timedelta
from graphql import GraphQLError
from ad.models import Course, CourseChapter

class CourseChapterType(DjangoObjectType):
    class Meta:
        model = CourseChapter
        fields = ('id', 'title', 'description', 'duration','course')

class CourseChapterDataModelType(graphene.ObjectType):
    rows = graphene.List(CourseChapterType)
    total_rows = graphene.Int()

class Query(graphene.ObjectType):
    all_chapters_list = graphene.Field(
        CourseChapterDataModelType,
        first = graphene.Int(),
        search = graphene.String(),
        skip = graphene.Int()
    ) 
    course_chapter_by_id = graphene.Field(CourseChapterType, chapter_id = graphene.Int(required=True))

    def resolve_course_chapter_by_id(self, info, chapter_id):
        return CourseChapter.objects.get(pk=chapter_id)
    
    def resolve_all_chapters_list(self, info, **kwargs):
        first = kwargs.get('first')
        search = kwargs.get('search')
        skip = kwargs.get('skip')

        filter = Q(is_deleted=False)

        if search:
            filter &= Q(title__icontains = search)
        
        qs = CourseChapter.objects.filter(filter).order_by("-created_date")
        total_count = qs.count()

        if skip:
            qs = qs[skip:]

        if first:
            qs = qs[:first]
        
        return CourseChapterDataModelType(rows = qs, total_rows = total_count)

class CreateChapter(graphene.Mutation):
    class Arguments:
        course_id = graphene.Int(required=True)
        title = graphene.String(required = True)
        duration = graphene.String(required=True)
        description = graphene.String()

    success = graphene.Boolean()
    chapter = graphene.Field(CourseChapterType)

    def mutate(self, info, course_id, **kwargs):
        course_instance = None
        try:
            course_instance = Course.objects.get(pk=course_id)
            course_chapter = CourseChapter.objects.create(course = course_instance, **kwargs)
            return CreateChapter(success = True, chapter = course_chapter)
        
        except Course.DoesNotExist:
            raise Exception(f"Course with the id {course_id} does not exist.")


class UpdateChapter(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        description = graphene.String()

    chapter = graphene.Field(CourseChapterType)  
    success = graphene.Boolean()

    def mutate(self, info, id, **kwargs):
        try:
            chapter = CourseChapter.objects.get(pk=id)
            for key,value in kwargs.items():
                setattr(chapter, key, value)
            chapter.save(update_fields=kwargs.keys())

            return UpdateChapter(chapter = chapter, success = True)
        except CourseChapter.DoesNotExist:
            raise Exception(f"Course with id {id} does not exists.")

class DeleteChapter(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, id):
        try:
            chapter = CourseChapter.objects.get(pk = id)
            chapter.is_deleted = True
            chapter.save(update_fields=['is_deleted'])
            return DeleteChapter(success = True, message=f"Id {id} {chapter.title} is deleted successfully.")
        
        except CourseChapter.DoesNotExist:
            raise Exception(f"Chapter with the id {id} does not exist.")
        
class Mutation(graphene.ObjectType):
    create_chapter = CreateChapter.Field()
    update_chapter = UpdateChapter.Field()
    delete_chapter = DeleteChapter.Field()

course_chapter_schema = graphene.Schema(query = Query, mutation = Mutation)