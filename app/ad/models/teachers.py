from django.db import models
from core.base import BaseModelV2
import uuid


class Teacher(BaseModelV2):
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    email = models.EmailField(unique=True)
    qualification = models.CharField(max_length = 50, default="N/A")
    unique_id = models.UUIDField(default=uuid.uuid4, unique = True, editable=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"