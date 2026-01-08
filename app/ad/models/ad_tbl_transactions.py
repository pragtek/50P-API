from django.db import models
from core.base import BaseModelV2
import uuid
from django.conf import settings

class TokenTransactions(BaseModelV2):
    module_code = models.CharField(max_length=25)
    unique_id = models.UUIDField(default=uuid.uuid4, editable = False, unique = True)
    STATUS_CHOICES = [
        ('new', 'New'),
        ('completed', 'Completed'),
        ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    tokens = models.IntegerField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
        related_name = "token_transactions",
        null = True,
        blank = True
    )

    class Meta:
        db_table = "tbl_transactions"
    
    def __str__(self):
        return f"{self.user.username} - {self.unique_id}-{self.status}{(self.tokens)}"