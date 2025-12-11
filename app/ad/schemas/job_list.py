import graphene
from graphene_django import DjangoObjectType
from ad.models.job import Job
from django.db.models import Q
from django.conf import settings

class JobListType(DjangoObjectType):
    class Meta:
        model = Job
        fields = "__all__"

class JobListDataModelType(graphene.ObjectType):
    total_rows = graphene.Int()
    rows = graphene.List(JobListType)


class JobListQuery(graphene.ObjectType):
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

class JobUserQuery(graphene.ObjectType):
    all_job_by_user =  graphene.Field(
        JobListDataModelType,
        first=graphene.Int(),
        search=graphene.String(),
        skip=graphene.Int(),

    )

    job_applied_with_id = graphene.Field(JobListType,
        job_id=graphene.Int(required=True),
    )

    def resolve_all_job_by_user(self, info , **kwargs):
        first = kwargs.get("first")
        skip = kwargs.get("skip")
        user = info.context.user
        search = kwargs.get("search")

        if user.is_anonymous:
            return JobListDataModelType(total_rows=0, rows=[])

        all_items = user.applied_jobs.all().order_by("-created_date")

        filter = Q()
        if search:
            filter = Q(job_title__icontains=search) | Q(description__icontains=search)
        all_items = all_items.filter(filter)
        total_count = all_items.count()

        if skip:
            all_items = all_items[skip:]
        if first:
            all_items = all_items[:first]

        return JobListDataModelType(
            total_rows=total_count,
            rows=all_items
        )
    
    def resolve_job_applied_with_id(self, info, job_id):
        user = info.context.user
        try:
            return user.applied_jobs.get(job_id=job_id)
        except Job.DoesNotExist:
            return None
        
class Query(JobUserQuery, JobListQuery, graphene.ObjectType):
    pass
  
job_list_schema = graphene.Schema(query=Query) 