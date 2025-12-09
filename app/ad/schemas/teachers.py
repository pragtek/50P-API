import graphene
from ad.models import Teacher
from graphene_django import DjangoObjectType
from django.db.models import Q


class TeacherType(DjangoObjectType):
    class Meta:
        model = Teacher
        fields = ( 
            "id",
            "unique_id",
            "first_name",
            "last_name",
            "email",
            "qualification"
        )


class TeacherDataModelType(graphene.ObjectType):
    total_rows = graphene.Int()
    rows = graphene.List(TeacherType)
    

class Query(graphene.ObjectType):
    all_teachers_by_id = graphene.Field(TeacherType, id = graphene.Int())
    all_teachers = graphene.Field(
        TeacherDataModelType,
        first = graphene.Int(),
        search = graphene.String(),
        skip = graphene.Int()
    )
    
    def resolve_all_teachers_by_id(self, info, id):
        return Teacher.objects.get(pk = id)

    def resolve_all_teachers(self, info, **kwargs):
        first = kwargs.get("first")
        search = kwargs.get("search")
        skip = kwargs.get("skip")

        filter = Q()

        if search:
            filter = Q(first_name__icontains = search)      
        all_teachers = Teacher.objects.filter(filter)
        all_teachers = all_teachers.order_by("-created_date")
        totalCount = all_teachers.count()

        if first:
            all_teachers = all_teachers[:first]
        
        if skip:
            all_teachers = all_teachers[skip:]
        
        return TeacherDataModelType(
            total_rows = totalCount,
            rows = all_teachers
        )
    
class CreateTeacher(graphene.Mutation):#qqq
    class Arguments:
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        email = graphene.String(required=True)
        qualification = graphene.String(required=True)
    
    teacher = graphene.Field(TeacherType)

    
    def mutate(self, info, **kwargs):
        new_teacher = Teacher.objects.create(
            first_name = kwargs.get("first_name"),
            last_name = kwargs.get("last_name"),
            email = kwargs.get("email"),
            qualification = kwargs.get("qualification"),
        )
        return CreateTeacher(teacher = new_teacher)

class UpdateTeacher(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        email = graphene.String(required=True)
        qualification = graphene.String(required=True)
    
    teacher = graphene.Field(TeacherType)

    
    def mutate(self, info, id, **kwargs):
        try:
            item = Teacher.objects.get(pk = id)
        except Teacher.DoesNotExist:
            raise Exception(f"Teacher with the ID {id} is not found.")
        
        item.first_name = kwargs.get("first_name")
        item.last_name = kwargs.get("last_name")
        item.email = kwargs.get("email")
        item.qualification = kwargs.get("qualification")
        item.save(
            update_fields=[
                "first_name",
                "last_name",
                "email",
                "qualification"
            ]
        )
        return UpdateTeacher(teacher = item)

class DeleteTeacher(graphene.Mutation):
    class Arguments:
        id = graphene.Int()
    
    ok = graphene.Boolean()

    def mutate(self, info, id):
        try:
            item = Teacher.objects.get(pk=id)
        except Teacher.DoesNotExist:
            raise Exception(f"Teacher with the ID{id} does not exist.")
        
        item.is_deleted = True
        item.save(
            update_fields=["is_deleted"]
        )
        return DeleteTeacher(ok = True)


class Mutation(graphene.ObjectType):
    add_teacher = CreateTeacher.Field()
    update_teacher = UpdateTeacher.Field()
    delete_teacher = DeleteTeacher.Field()

teachers_schema = graphene.Schema(query = Query, mutation = Mutation)