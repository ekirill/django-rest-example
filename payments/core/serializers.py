from core.models import Account, Payment
from rest_framework import serializers


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('id', 'owner', 'balance', 'currency')


class PaymentSerializer(serializers.ModelSerializer):
    direction = serializers.CharField(required=False)

    class Meta:
        model = Payment
        fields = ('to_account', 'from_account', 'direction', 'amount', 'currency')

    def create(self, validated_data):
        payments = validated_data['from_account'].pay(
            validated_data['to_account'], validated_data['amount'], validated_data['currency']
        )
        return payments[0]
