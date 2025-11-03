import graphene
from graphene_django import DjangoObjectType
from ad.models import TokenTransactions
from graphql_jwt.decorators import login_required


class TokenTransactionsType(DjangoObjectType):
    class Meta:
        model = TokenTransactions
        fields = ("module_code", "unique_id", "status", "tokens")

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



class Mutation(graphene.ObjectType):
    add_transaction = CreateTransaction.Field()


transactions_schema = graphene.Schema(query = Query, mutation = Mutation)