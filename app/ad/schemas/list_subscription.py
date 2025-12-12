import graphene
from graphene_django import DjangoObjectType
from ad.models import Subscription
from django.db.models import Q

class SubscriptionType(DjangoObjectType):
    class Meta:
        model = Subscription
        fields = [
            'subscription_id',
            'user',
            'course',
            'subscription_type',
            'is_active',
            'price',
            'payment_status',
            'transaction_id'
        ]

class SubscriptionDataModelType(graphene.ObjectType):
    rows = graphene.List(SubscriptionType)
    total_rows = graphene.Int()

class Query(graphene.ObjectType):
    list_subscription = graphene.Field(
        SubscriptionDataModelType,
        first = graphene.Int(),
        search = graphene.String(),
        skip = graphene.Int()
        )
    
    def resolve_list_subscription(self, info, **kwargs):
        first = kwargs.get('first')
        search = kwargs.get('search')
        skip = kwargs.get('skip')

        filter = Q()

        if search:
            filter = Q(user__icontains = search)
        
        list_subscription = Subscription.objects.filter(filter)
        total_rows = list_subscription.count()
        list_subscription = list_subscription.order_by('-created_date')

        if first:
            list_subscription = list_subscription[:first]
        
        if skip:
            list_subscription = list_subscription[skip:]
        
        return SubscriptionDataModelType(
            rows = list_subscription,
            total_rows = total_rows
        )

list_subscription_schema = graphene.Schema(query = Query)