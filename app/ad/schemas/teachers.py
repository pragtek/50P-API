import graphene
from ad.models import Teacher
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required


class TeacherType(DjangoObjectType):
    class Meta:
        model = Teacher
        fields = (
            "first_name",
            "last_name",
            "email"
        )


class TeacherDataModelType(graphene.ObjectType):
    total_rows = graphene.Int()
    rows = graphene.List(TeacherType)

class Query(grapheme.ObjectType):
    all_teacher_by_id = graphene.Field(TeacherType, id = graphene.Int())
    all_teachers = graphene.Field(
        TeacherDataModelType,
        first = graphene.Int(),
        search = graphene.String(),
        skip = graphene.Int()
    )
    