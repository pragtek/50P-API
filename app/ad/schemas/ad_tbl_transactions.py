import graphene
from graphene_django import DjangoObjectType
from ad.models import TokenTransactions
from graphql_jwt.decorators import login_required
from django.core.exceptions import ValidationError


class TokenTransactionsType(DjangoObjectType):
    class Meta:
        model = TokenTransactions
        fields = ("id", "module_code", "unique_id", "status", "tokens")

class TokenTransactionsDataModelType(graphene.ObjectType):
    total_rows = graphene.Int()
    rows = graphene.List(TokenTransactionsType)


    
class Query(graphene.ObjectType):
    all_tokens_transactions = graphene.Field(TokenTransactionsDataModelType)
    
    def resolve_all_tokens_transactions(self,info):
        all_transactions = TokenTransactions.objects.all()
        return TokenTransactionsDataModelType(
            total_rows = all_transactions.count(),
            rows = all_transactions
            )

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




class Mutation(graphene.ObjectType):
    add_transaction = CreateTransaction.Field()
    update_transaction = UpdateTransaction.Field()


transactions_schema = graphene.Schema(query = Query, mutation = Mutation)