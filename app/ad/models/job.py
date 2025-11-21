from django.db import models
from core.base import BaseModelV2

class Job(BaseModelV2):

    EMPLOYMENT_TYPE_CHOICES = [
        ('full-time', 'Full-Time'),
        ('part-time', 'Part-Time'),
    ]
    job_id = models.AutoField(primary_key=True)
    job_title = models.CharField(max_length=255)
    description = models.TextField()
    qualification = models.TextField()
    location = models.CharField(max_length=255)
    salary = models.CharField(max_length=100)
    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default='full-time'
    )

    category = models.CharField(max_length=100)
    experience = models.CharField(max_length=100)

    class Meta:
        db_table = "tbl_jobs"

    def __str__(self):
        return f"{self.job_title} - {self.location}"