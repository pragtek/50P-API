import graphene
from graphene_django import DjangoObjectType
from ad.models.job import Job
from django.db.models import Q
from django.conf import settings
from graphql import GraphQLError
from django.contrib.auth import get_user_model

User = get_user_model()

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
        user_id = graphene.Int(required=True),
        first=graphene.Int(),
        search=graphene.String(),
        skip=graphene.Int(),

    )

    job_applied_with_id = graphene.Field(JobListType,
        job_id=graphene.Int(required=True),
        user_id=graphene.Int(required=True),
    )

    def resolve_all_job_by_user(self, info , user_id,**kwargs):
        first = kwargs.get("first")
        skip = kwargs.get("skip")
        search = kwargs.get("search")

        try:
            user = User.objects.get(pk=user_id)

        except User.DoesNotExist:
            return JobListDataModelType(
                total_rows=0,
                rows=[]
            )

       

        all_items = user.applied_jobs.all().order_by("-created_date")

        filter = Q()
        if search:
            all_items = all_items.filter(
                Q(job_title__icontains=search) | Q(description__icontains=search)
            )
        total_count = all_items.count()

        if skip:
            all_items = all_items[skip:]
        if first:
            all_items = all_items[:first]

        return JobListDataModelType(
            total_rows=total_count,
            rows=all_items
        )

    def resolve_job_applied_with_id(self, info, job_id, user_id):
        user = User.objects.get(pk=user_id)
        try:
            return user.applied_jobs.get(job_id=job_id)
        except Job.DoesNotExist:
            return None
        
class Query(JobUserQuery, JobListQuery, graphene.ObjectType):
    pass



class ApplyJobMutation(graphene.Mutation):
    class Arguments:
        job_id = graphene.Int(required=True)
        user_id = graphene.Int(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, job_id, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise GraphQLError("User does not exist.")
        
        try:
            job = Job.objects.get(pk=job_id)
        except Job.DoesNotExist:
            raise GraphQLError("Job does not exist.")
        
        if job.applicants.filter(pk=user.pk).exists():
            raise GraphQLError("User has already applied for this job.")
        
        job.applicants.add(user)

        return ApplyJobMutation(
            success = True,
            message = "Job application successful."
        )

class Mutation(graphene.ObjectType):
    apply_job = ApplyJobMutation.Field()




job_list_schema = graphene.Schema(query=Query, mutation=Mutation) 