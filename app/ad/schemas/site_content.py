import graphene
from graphene_django import DjangoObjectType
from ad.models.site_content import SiteContent
from django.db.models import Q
from graphql import GraphQLError


class SiteContentType(DjangoObjectType):
    class Meta:
        model = SiteContent
        fields = (
            "id", 
            "title",
            "content",
        )


class SiteContentDataModelType(graphene.ObjectType):
    total_rows = graphene.Int()
    rows = graphene.List(SiteContentType)


class Query(graphene.ObjectType):
    all_content = graphene.Field(
        SiteContentDataModelType,
        first = graphene.Int(),
        search = graphene.String(),
        skip = graphene.Int()
    )
    content_by_id = graphene.Field(SiteContentType, id = graphene.Int(required=True))

    def resolve_all_content(self,info, **kwargs):
        first = kwargs.get("first")
        skip = kwargs.get("skip")
        search = kwargs.get("search")
        
        filter = Q()

        if search:
            filter = Q(title__icontains = search)

        all_content = SiteContent.objects.filter(filter)
        totalCount = all_content.count()

        if skip:
            all_content = all_content[skip:]

        if first:
            all_content = all_content[:first]

        return SiteContentDataModelType(
            total_rows = totalCount,
            rows = all_content
        )

    
    def resolve_content_by_id(self,info, id):
        return SiteContent.objects.get(id=id)


class CreateContent(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        content = graphene.String(required=True)

    site_content = graphene.Field(SiteContentType)
    success = graphene.Boolean()
    
    def mutate(self, info, title, content):
        try:
            site_content = SiteContent.objects.create(
                title=title,
                content=content
            )
        except Exception as e:
            raise GraphQLError(f"Error creating content: {str(e)}") 
        
        return CreateContent(site_content=site_content, success=True)
    
class UpdateContent(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        content = graphene.String()

    site_content = graphene.Field(SiteContentType)
    success = graphene.Boolean()

    def mutate(self, info, id, title = None, content = None):
        try:
            site_content = SiteContent.objects.get(id=id)
        except SiteContent.DoesNotExist:
            raise GraphQLError(f"Content with ID {id} does not exist.")
        
        if title is not None:
            site_content.title = title

        if content is not None:
            site_content.content = content

        site_content.save()

        return UpdateContent(site_content=site_content, success=True)
    

class DeleteContent(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id):
        try:
            site_content = SiteContent.objects.get(id=id)
        except SiteContent.DoesNotExist:
            raise GraphQLError(f"Content with ID {id} does not exist.")
        
        site_content.is_deleted = True
        site_content.save(update_fields=["is_deleted"])
        return DeleteContent(ok=True)
    
class Mutation(graphene.ObjectType):
    create_content = CreateContent.Field()
    update_content = UpdateContent.Field()
    delete_content = DeleteContent.Field()

site_content_schema = graphene.Schema(query=Query, mutation=Mutation)
