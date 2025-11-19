from django.db import models
from django.conf import settings

from core.base import BaseModelV2
# from .course import Course
from .ad_tbl_transactions import TokenTransactions


class Subscription(BaseModelV2):
    subscription_id = models.AutoField(primary_key=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions", 
        null=True,
        blank=True
    )

    # course= models.ForeignKey(
    #     Course,
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name="subscriptions"
    # )

    subscription_type = models.CharField(
        max_length=50,
        choices=[
            ("free", "Free"),
            ("paid", "Paid"),
            ("premium", "Premium"),
        ],       default="free"

    )

    is_active = models.BooleanField(default=True)

    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    payment_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("completed", "Completed"),
            ("failed", "Failed"),
            ("cancelled", "Cancelled"),
        ],
        default="pending"
    )


    transaction_id = models.ForeignKey(TokenTransactions, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Subscription {self.SubscriptionID} ({self.SubscriptionType})"
