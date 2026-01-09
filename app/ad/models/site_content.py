from django.db import models
from core.base import BaseModelV2

class SiteContent(BaseModelV2):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        return f"{self.title}"