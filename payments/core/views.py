from rest_framework import generics, mixins

from core.models import Account
from core.serializers import AccountSerializer


class AccountsList(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
