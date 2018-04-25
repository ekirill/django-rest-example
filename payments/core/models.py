from decimal import Decimal

from core.errors import InvalidAccountCurrency, InvalidAmount, InsufficientBalance
from django.db import models, transaction
from django.utils.translation import ugettext_lazy

from .const import CURRENCIES, PAYMENT_DIRECTIONS, PAYMENT_DIRECTIONS_OUTGOING, PAYMENT_DIRECTIONS_INCOMING

CURRENCY_CHOICES = tuple((_c, _c) for _c in CURRENCIES)
PAYMENT_DIRECTION_CHOICES = tuple((_d, _d) for _d in PAYMENT_DIRECTIONS)


class Account(models.Model):
    class Meta:
        verbose_name = "Account"
        ordering = ['pk']

    id = models.CharField(verbose_name=ugettext_lazy("Account ID"), max_length=200, primary_key=True)
    owner = models.CharField(verbose_name=ugettext_lazy("Account owner ID"), max_length=200)
    balance = models.DecimalField(verbose_name=ugettext_lazy("Balance"), max_digits=20, decimal_places=4, default=0)
    currency = models.CharField(verbose_name=ugettext_lazy("Currency"), max_length=5, choices=CURRENCY_CHOICES)

    def pay(self, to_account: 'Account', amount: Decimal, currency: str):
        """
        Make a payment, that transfers amount of money from this account to `to_account`.
        Raises InvalidAccountCurrency, InvalidAmount, InsufficientBalance
        :param to_account: destination account
        :param amount: positive Decimal with amount of transfer
        :param currency: currency of money
        """
        invalid_currency_acc_ids = []
        for acc in (self, to_account):
            if acc.currency != currency:
                invalid_currency_acc_ids.append(acc.pk)
        if invalid_currency_acc_ids:
            raise InvalidAccountCurrency(invalid_currency_acc_ids)

        if amount < 0:
            raise InvalidAmount()

        if amount > self.balance:
            raise InsufficientBalance()

        self.balance -= amount
        to_account.balance += amount
        payments = [
            Payment(
                to_account=to_account, from_account=self, direction=PAYMENT_DIRECTIONS_OUTGOING,
                amount=amount, currency=currency,
            ),
            Payment(
                to_account=self, from_account=to_account, direction=PAYMENT_DIRECTIONS_INCOMING,
                amount=amount, currency=currency,
            )
        ]

        with transaction.atomic():
            self.save(update_fields=('balance',))
            to_account.save(update_fields=('balance',))
            Payment.objects.bulk_create(payments)

        return payments


class Payment(models.Model):
    class Meta:
        verbose_name = "Payment"
        ordering = ['-pk']

    to_account = models.ForeignKey(
        Account, verbose_name="Payment destination account", on_delete=models.PROTECT,
        related_name="to_payments",
    )
    from_account = models.ForeignKey(
        Account, verbose_name="Payment source account", on_delete=models.PROTECT,
        related_name="from_payments",
    )
    direction = models.CharField(
        verbose_name=ugettext_lazy("Payment direction"), max_length=64, choices=PAYMENT_DIRECTION_CHOICES
    )

    amount = models.DecimalField(verbose_name=ugettext_lazy("Amount"), max_digits=20, decimal_places=4, default=0)
    currency = models.CharField(verbose_name=ugettext_lazy("Currency"), max_length=5, choices=CURRENCY_CHOICES)
