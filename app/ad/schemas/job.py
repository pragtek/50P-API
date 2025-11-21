import graphene
from graphene_django import DjangoObjectType
from django.db.models import Q
from ad.models.job import Job
from django.core.exceptions import ValidationError

class JobType(DjangoObjectType):
    class Meta:
        model = Job
        fields = (
            "job_id",
            "job_title",
            "description",
            "qualification",
            "location",
            "salary",
            "employment_type",
            "category",
            "experience",
        )

class JobDataModelType(graphene.ObjectType):
    total_rows = graphene.Int()
    rows = graphene.List(JobType)

class Query(graphene.ObjectType):
    all_jobs = graphene.Field(
        JobDataModelType,
        first = graphene.Int(),
        search = graphene.String(),
        skip = graphene.Int(),
    )
    job_by_id = graphene.Field(
        JobType,
        job_id = graphene.Int(required=True)
    )

    def resolve_all_jobs(self, info, **kwargs):
        search = kwargs.get("search")
        first = kwargs.get("first")
        skip = kwargs.get("skip")

        filter = Q()

        if search:
            filter = (Q(job_title__icontains=search) | Q(description__icontains=search) | Q(location__icontains=search) | Q(category__icontains=search))

        all_items = Job.objects.filter(filter).order_by("-created_date")
        total_count = all_items.count()

        if skip:
            all_items = all_items[skip:]

        if first:
            all_items = all_items[:first]

        return JobDataModelType(
            total_rows = total_count,
            rows = all_items
        )
    
    def resolve_job_by_id(self, info, job_id):
        return Job.objects.get(pk = job_id)
    
class CreateJob(graphene.Mutation):
    class Arguments:
        job_title = graphene.String(required=True)
        description = graphene.String(required=True)
        qualification = graphene.String(required=True)
        location = graphene.String(required=True)
        salary = graphene.String(required=True)
        employment_type = graphene.String(required=True)
        category = graphene.String(required=True)
        experience = graphene.String(required=True)

    job = graphene.Field(JobType)
    
    def mutate(self, info, **kwargs):
        job = Job.objects.create(
            job_title=kwargs.get("job_title"),
            description=kwargs.get("description"),
            qualification=kwargs.get("qualification"),
            location=kwargs.get("location"),
            salary=kwargs.get("salary"),
            employment_type=kwargs.get("employment_type"),
            category=kwargs.get("category"),
            experience=kwargs.get("experience"),
        )
        return CreateJob(job=job)
    
class UpdateJob(graphene.Mutation):
    class Arguments:
        job_id = graphene.Int(required=True)
        job_title = graphene.String()
        description = graphene.String()
        qualification = graphene.String()
        location = graphene.String()
        salary = graphene.String()
        employment_type = graphene.String()
        category = graphene.String()
        experience = graphene.String()

    job = graphene.Field(JobType)

    def mutate(self, info,job_id, **kwargs):
        try:
            job = Job.objects.get(pk=job_id)
        except Job.DoesNotExist:
            raise ValidationError("Job with the given ID does not exist.")
        job.job_title = kwargs.get("job_title", job.job_title)
        job.description = kwargs.get("description", job.description)
        job.qualification = kwargs.get("qualification", job.qualification)
        job.location = kwargs.get("location", job.location)
        job.salary = kwargs.get("salary", job.salary)
        job.employment_type = kwargs.get("employment_type", job.employment_type)
        job.category = kwargs.get("category", job.category)
        job.experience = kwargs.get("experience", job.experience)
        job.save(
            update_fields=[
                "job_title",
                "description",
                "qualification",
                "location",
                "salary",
                "employment_type",
                "category",
                "experience",
            ]
        )
        return UpdateJob(job=job)
    
class DeleteJob(graphene.Mutation):
    class Arguments:
        job_id = graphene.Int(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, job_id):
      try:
          job = Job.objects.get(pk=job_id)
      except Job.DoesNotExist:
          raise ValidationError("Job with the given ID does not exist.")
      job.is_deleted = True
      job.save(update_fields=["is_deleted"])
      return DeleteJob(ok=True)

class Mutation(graphene.ObjectType):
    create_job = CreateJob.Field()
    update_job = UpdateJob.Field()
    delete_job = DeleteJob.Field()

job_schema = graphene.Schema(query=Query, mutation=Mutation)
    