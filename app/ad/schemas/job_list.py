import graphene
from graphene_django import DjangoObjectType
from ad.models.job import Job
from django.db.models import Q

class JobListType(DjangoObjectType):
    class Meta:
        model = Job
        fields = ("job_id","job_title")

class JobListDataModelType(graphene.ObjectType):
    total_rows = graphene.Int()
    rows = graphene.List(JobListType)


class Query(graphene.ObjectType):
    all_job_list = graphene.Field(
        JobListDataModelType,
        first=graphene.Int(),
        search=graphene.String(),
        skip=graphene.Int(),
    )

    def resolve_all_job_list(root, info, **kwargs):
      search = kwargs.get("search")
      first = kwargs.get("first")
      skip = kwargs.get("skip")

      filter = Q()
      if search:
          filter = (Q(job_title__icontains=search))
      all_items = Job.objects.filter(filter).order_by("-created_date")
      total_count = all_items.count()

      if skip:
          all_items = all_items[skip:]
      if first:
          all_items = all_items[:first]

      return JobListDataModelType(
            total_rows=total_count,
            rows=all_items
      )  
    
    job_list_by_id = graphene.Field(
        JobListType,
        job_id=graphene.Int(required=True),
    )

    def resolve_job_list_by_id(self, info, job_id):
        try:
            return Job.objects.get(job_id=job_id)
        except Job.DoesNotExist:
            return None

job_list_schema = graphene.Schema(query=Query) 