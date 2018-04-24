from django.db import models
from django.utils.translation import ugettext_lazy

from .const import CURRENCIES, PAYMENT_DIRECTIONS


CURRENCY_CHOICES = tuple((_c, _c) for _c in CURRENCIES)
PAYMENT_DIRECTION_CHOICES = tuple((_d, _d) for _d in PAYMENT_DIRECTIONS)


class Account(models.Model):
    class Meta:
        verbose_name = "Account"

    id = models.CharField(verbose_name=ugettext_lazy("Account ID"), max_length=200, primary_key=True)
    owner = models.CharField(verbose_name=ugettext_lazy("Account owner ID"), max_length=200)
    balance = models.DecimalField(verbose_name=ugettext_lazy("Balance"), max_digits=20, decimal_places=4, default=0)
    currency = models.CharField(verbose_name=ugettext_lazy("Currency"), max_length=5, choices=CURRENCY_CHOICES)


class Payment(models.Model):
    class Meta:
        verbose_name = "Payment"

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
