import graphene
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required
from ad.models import Subscription
from django.core.exceptions import ValidationError
from django.db.models import Q
from authtf.models.user import User
from django.core.exceptions import ObjectDoesNotExist
from ad.models.ad_tbl_transactions import TokenTransactions
# from ad.models.courses import Course

class SubscriptionType(DjangoObjectType):
    class Meta:
        model = Subscription
        fields = (
            "subscription_id",
            "user",
            # "course",
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
        # course_id =  graphene.Int(required=True)
        subscription_type = graphene.String(required=True)
        is_active = graphene.Boolean(required=True)
        price = graphene.Float(required=True)
        payment_status = graphene.String(required=True)
        transaction_id = graphene.String(required=True)
    
    subscription = graphene.Field(SubscriptionType)

    
    def mutate(self, info, **kwargs):
        user_instance = None
        try:
            user_instance = User.objects.get(id=kwargs.get("user_id"))
        except ObjectDoesNotExist:
            raise ValidationError("User with the given ID does not exist.")
        transaction_instance = None
        try:
            transaction_instance = TokenTransactions.objects.get(id=kwargs.get("transaction_id"))
        except ObjectDoesNotExist:
            raise ValidationError("Transaction with the given ID does not exist.")

        # course = Course.objects.get(id=kwargs.get("course_id"))

        new_subscription = Subscription.objects.create(
            user = user_instance,
            # course = course,
            subscription_type = kwargs.get("subscription_type"),
            is_active = kwargs.get("is_active", False),
            price = kwargs.get("price"),
            payment_status = kwargs.get("payment_status"),
            transaction_id = transaction_instance,
        )

        return Query.CreateSubscription(subscription=new_subscription)
    
class UpdateSubscription(graphene.Mutation):
    class Arguments:
        subscription_id = graphene.Int(required=True)
        user_id = graphene.Int()
        # course_id = graphene.Int()
        subscription_type = graphene.String()
        is_active = graphene.Boolean()
        price = graphene.Float()
        payment_status = graphene.String()
        transaction_id = graphene.String()

    subscription = graphene.Field(SubscriptionType)

    
    def mutate(self, info, subscription_id, **kwargs):
       try:
           item = Subscription.objects.get(subscription_id=subscription_id)
       except Subscription.DoesNotExist:
            raise ValidationError("Subscription with the given ID does not exist.")
    #    hello
    #ABCD
      

       user_id = kwargs.get("user_id")
       transaction_id = kwargs.get("transaction_id")
       if transaction_id is not None:
           try:
            transaction_instance = TokenTransactions.objects.get(id=transaction_id)
            item.transaction_id = transaction_instance
           except ObjectDoesNotExist:
                raise ValidationError("Transaction with the given ID does not exist.")
       if user_id is not None:
           try:
                user_instance = User.objects.get(id=user_id)
                item.user = user_instance
                
           except ObjectDoesNotExist:
                raise ValidationError("User with the given ID does not exist.")
          
    #    if "course_id" in kwargs:
    #           item.course = Course.objects.get(id=kwargs["course_id"])
    #           update_filelds.append("course")
       if "subscription_type" in kwargs:
           item.subscription_type = kwargs["subscription_type"]
          
       if "is_active" in kwargs:
           item.is_active = kwargs["is_active"]
          
       if "price" in kwargs:
           item.price = kwargs["price"]
          
       if "payment_status" in kwargs:
           item.payment_status = kwargs["payment_status"]
       
           

       item.save(update_fields=["user", "price", "is_active", "subscription_type", "payment_status", "transaction_id"])
       return UpdateSubscription(subscription=item)
    
class DeleteSubscription(graphene.Mutation):
    class Arguments:
        subscription_id = graphene.Int(required=True)

    ok = graphene.Boolean()

    
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
       
