import graphene
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required
from ad.models import Subscription
from django.core.exceptions import ValidationError
from django.db.models import Q
from authtf.models.user import User
from ad.models.courses import Course

class SubscriptionType(DjangoObjectType):
    class Meta:
        model = Subscription
        fields = (
            "subscription_id",
            "user",
            "course",
            "subscription_type",
            "is_active",
            "price",
            "payment_status",
            "transaction_id",
        )

class SubscriptionDataModelType(graphene.ObjectType):
    total_rows = graphene.Int()
    rows = graphene.List(SubscriptionType)

class Query(graphene.ObjectType):
    subscription_by_id = graphene.Field(
        SubscriptionType,
        subscription_id = graphene.Int()
    )
    all_subscriptions = graphene.Field(
        SubscriptionDataModelType,
        first = graphene.Int(),
        search = graphene.String(),
        skip = graphene.Int(),
    )

    def resolve_subscription_by_id(self, info, subscription_id):
      try: 
          return Subscription.objects.get(subscription_id = subscription_id)
      except Subscription.DoesNotExist:
            raise ValidationError("Subscription with the given ID does not exist.")
      
    def resolve_all_subscriptions(self, info, **kwargs):
        search = kwargs.get("search")
        first = kwargs.get("first")
        skip = kwargs.get("skip")

        filter = Q()
        if search:
            filter = (Q(subscription_type__icontains=search) | Q(payment_status__icontains=search) | Q(transaction_id__icontains=search))

        all_items = Subscription.objects.filter(filter).order_by("-created_date")
        total_count = all_items.count()

        if skip:
            all_items = all_items[skip:]
        if first:
            all_items = all_items[:first]

        return SubscriptionDataModelType(total_rows = total_count, rows = all_items)
    
class CreateSubscription(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int(required=True)
        course_id =  graphene.Int(required=True)
        subscription_type = graphene.String(required=True)
        is_active = graphene.Boolean(required=True)
        price = graphene.Float(required=True)
        payment_status = graphene.String(required=True)
        transaction_id = graphene.String(required=True)
    
    subscription = graphene.Field(SubscriptionType)

    @login_required
    def mutate(self, info, **kwargs):
        session_user = info.context.user

        user = User.objects.get(id=kwargs.get("user_id"))
        course = Course.objects.get(id=kwargs.get("course_id"))

        new_subscription = Subscription.objects.create(
            user = user,
            course = course,
            subscription_type = kwargs.get("subscription_type"),
            is_active = kwargs.get("is_active", False),
            price = kwargs.get("price"),
            payment_status = kwargs.get("payment_status"),
            transaction_id = kwargs.get("transaction_id"),
        )

        return Query.CreateSubscription(subscription=new_subscription)
    
class UpdateSubscription(graphene.Mutation):
    class Arguments:
        subscription_id = graphene.Int(required=True)
        user_id = graphene.Int()
        course_id = graphene.Int()
        subscription_type = graphene.String()
        is_active = graphene.Boolean()
        price = graphene.Float()
        payment_status = graphene.String()
        transaction_id = graphene.String()

    subscription = graphene.Field(SubscriptionType)

    @login_required
    def mutate(self, info, subscription_id, **kwargs):
       try:
           item = Subscription.objects.get(subscription_id=subscription_id)
       except Subscription.DoesNotExist:
            raise ValidationError("Subscription with the given ID does not exist.")
       
       update_filelds = []

       if "user_id" in kwargs:
           item.user = User.objects.get(id=kwargs["user_id"])
           update_filelds.append("user")
       if "course_id" in kwargs:
              item.course = Course.objects.get(id=kwargs["course_id"])
              update_filelds.append("course")
       if "subscription_type" in kwargs:
           item.subscription_type = kwargs["subscription_type"]
           update_filelds.append("subscription_type")
       if "is_active" in kwargs:
           item.is_active = kwargs["is_active"]
           update_filelds.append("is_active")
       if "price" in kwargs:
           item.price = kwargs["price"]
           update_filelds.append("price")
       if "payment_status" in kwargs:
           item.payment_status = kwargs["payment_status"]
           update_filelds.append("payment_status")
       if "transaction_id" in kwargs:
           item.transaction_id = kwargs["transaction_id"]
           update_filelds.append("transaction_id")

       item.save(update_fields=update_filelds)
       return UpdateSubscription(subscription=item)
    
class DeleteSubscription(graphene.Mutation):
    class Arguments:
        subscription_id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @login_required
    def mutate(self, info, subscription_id):
        try:
            item = Subscription.objects.get(subscription_id=subscription_id)
        except Subscription.DoesNotExist:
            raise ValidationError("Subscription with the given ID does not exist.")
        
        item.is_deleted = True
        item.save(update_fields=["is_deleted"])
        return DeleteSubscription(ok=True)
    
class Mutation(graphene.ObjectType):
    add_subscription = CreateSubscription.Field()
    update_subscription = UpdateSubscription.Field()
    delete_subscription = DeleteSubscription.Field()

subscription_schema = graphene.Schema(query=Query, mutation=Mutation)
       
