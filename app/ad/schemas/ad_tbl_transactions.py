import graphene
from graphene_django import DjangoObjectType
from ad.models import TokenTransactions
from graphql_jwt.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Q
from authtf.models.user import User

class TokenTransactionsType(DjangoObjectType):
    class Meta:
        model = TokenTransactions
        fields = ("id", "module_code", "unique_id", "status", "tokens", "user")

class TokenTransactionsDataModelType(graphene.ObjectType):
    total_rows = graphene.Int()
    rows = graphene.List(TokenTransactionsType)


    
class Query(graphene.ObjectType):
    all_tokens_transactions_by_id = graphene.Field(TokenTransactionsType, id = graphene.Int())

    all_tokens_transactions = graphene.Field(
        TokenTransactionsDataModelType,
        first = graphene.Int(),
        search = graphene.String(),
        skip = graphene.Int(),
    )



    
    def resolve_all_tokens_transactions(self, info, **kwargs):
        first = kwargs.get("first")
        search = kwargs.get("search")
        skip = kwargs.get("skip")

        filter = Q()

        if search:
            filter =  Q(module_code__icontains = search)
        
        all_transactions = TokenTransactions.objects.filter(filter)
        all_transactions = all_transactions.order_by("-created_date")
        totalCount = all_transactions.count()

        if skip:
            all_transactions = all_transactions[skip:]

        if first:
            all_transactions = all_transactions[:first] 

        return TokenTransactionsDataModelType(
            total_rows = totalCount,
            rows = all_transactions
            )

    def resolve_all_tokens_transactions_by_id(self, info, id):
        return TokenTransactions.objects.get(pk = id)

class CreateTransaction(graphene.Mutation):
    class Arguments:
        module_code = graphene.String(required = True)
        status = graphene.String(required = True)
        tokens = graphene.Int(required = True)
    
    transaction = graphene.Field(TokenTransactionsType)

    def mutate(self, info, **kwargs):
        
        new_transaction = TokenTransactions.objects.create(
            module_code = kwargs.get("module_code"),
            status = kwargs.get("status"),
            tokens = kwargs.get("tokens"),
            
        )

        return CreateTransaction(transaction = new_transaction)

class UpdateTransaction(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required = True)
        module_code = graphene.String()
        status = graphene.String()
        tokens = graphene.Int()
    
    transaction = graphene.Field(TokenTransactionsType)

    def mutate(self, info, id, module_code = None, status = None, tokens = None):
        try:
            item = TokenTransactions.objects.get(pk = id)
        except TokenTransactions.DoesNotExist:
            raise ValidationError("Transaction does not exists.")
        
        if module_code is not None:
            item.module_code = module_code
        
        if status is not None:
            item.status = status
        
        if tokens is not None:
            item.tokens = tokens

        item.save(
            update_fields = [
            "module_code",
            "status",
            "tokens"
            ]
        )
        return UpdateTransaction(transaction = item)


class DeleteTransaction(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required = True)
    
    ok = graphene.Boolean()

    def mutate(self, info, id):
        try:
            item = TokenTransactions.objects.get(pk = id)
        
        except TokenTransactions.DoesNotExist:
            raise ValidationError("Transaction does not exist.")

        item.is_deleted = True
        item.save(update_fields=["is_deleted"])
        return DeleteTransaction(ok = True)
    
class DoTransaction(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int(required = True)
        tokens = graphene.Int(required=True)
        module_code = graphene.String(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    transaction = graphene.Field(TokenTransactionsType)

    def mutate(self, info, user_id, tokens, module_code):
        try:
            user_obj = User.objects.get(pk=user_id)
            txn = TokenTransactions.objects.create(
                tokens = tokens,
                module_code = module_code,
                user = user_obj
            )
            return DoTransaction(success=True, message="Transaction successful.", transaction = txn)
        except User.DoesNotExist:
            return  DoTransaction(success = False, message = f"User with ID {user_id} not found.")
        
        except Exception as e:
            return DoTransaction(success=False, message=str(e))
        

class Mutation(graphene.ObjectType):
    add_transaction = CreateTransaction.Field()
    update_transaction = UpdateTransaction.Field()
    delete_transaction = DeleteTransaction.Field()
    do_transaction = DoTransaction.Field()

transactions_schema = graphene.Schema(query = Query, mutation = Mutation)