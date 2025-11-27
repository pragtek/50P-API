import graphene
from graphene_django import DjangoObjectType
from ad.models import TokenTransactions
from graphql_jwt.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Q
#a
class TokenTransactionsType(DjangoObjectType):
    class Meta:
        model = TokenTransactions
        fields = ("id", "module_code", "unique_id", "status", "tokens")

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

    @login_required
    def mutate(self, info, **kwargs):
        session_user = info.context.user
        new_transaction = TokenTransactions.objects.create(
            module_code = kwargs.get("module_code"),
            status = kwargs.get("status"),
            tokens = kwargs.get("tokens"),
            user = session_user
        )

        return CreateTransaction(transaction = new_transaction)

class UpdateTransaction(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required = True)
        module_code = graphene.String()
        status = graphene.String()
        tokens = graphene.Int()
    
    transaction = graphene.Field(TokenTransactionsType)

    @login_required
    def mutate(self, info, id, **kwargs):
        try:
            item = TokenTransactions.objects.get(pk = id, user = info.context.user)
        except TokenTransactions.DoesNotExist:
            raise ValidationError("Transaction does not exists.")
        
        item.module_code = kwargs.get("module_code")
        item.status = kwargs.get("status")
        item.tokens = kwargs.get("tokens")
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

    @login_required
    def mutate(self, info, id):
        try:
            item = TokenTransactions.objects.get(pk = id, user = info.context.user)
        
        except TokenTransactions.DoesNotExist:
            raise ValidationError("Transaction does not exist.")

        item.is_deleted = True
        item.save(update_fields=["is_deleted"])
        return DeleteTransaction(ok = True)

class Mutation(graphene.ObjectType):
    add_transaction = CreateTransaction.Field()
    update_transaction = UpdateTransaction.Field()
    delete_transaction = DeleteTransaction.Field()


transactions_schema = graphene.Schema(query = Query, mutation = Mutation)