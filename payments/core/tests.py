from decimal import Decimal

from core.errors import InvalidAccountCurrency, InvalidAmount, InsufficientBalance
from django.test import TestCase
from rest_framework.test import APIClient

from core.const import CURRENCY_PHP, PAYMENT_DIRECTIONS_INCOMING, CURRENCY_USD, PAYMENT_DIRECTIONS_OUTGOING
from core.models import Account, Payment


class AccountsTestCase(TestCase):
    accounts_url = '/v1/accounts'

    def setUp(self):
        self.client = APIClient()

        self.owner_1 = 'owner_1'
        self.owner_2 = 'owner_2'

        self.accounts = (
            Account(id='acc_1', owner=self.owner_1, balance=0, currency=CURRENCY_PHP),
            Account(id='acc_2', owner=self.owner_1, balance=100, currency=CURRENCY_PHP),
            Account(id='acc_3', owner=self.owner_2, balance=200, currency=CURRENCY_PHP),
            Account(id='acc_4', owner=self.owner_2, balance=200, currency=CURRENCY_USD),
        )
        Account.objects.bulk_create(self.accounts)

        self.empty_account, self.to_account, self.from_account, self.usd_account = self.accounts

    def test_accounts_list_methods(self):
        response = self.client.put(self.accounts_url, format='json')
        self.assertEqual(response.status_code, 405)

        response = self.client.post(self.accounts_url, format='json')
        self.assertEqual(response.status_code, 405)

        response = self.client.patch(self.accounts_url, format='json')
        self.assertEqual(response.status_code, 405)

        response = self.client.delete(self.accounts_url, format='json')
        self.assertEqual(response.status_code, 405)

        response = self.client.get(self.accounts_url, format='json')
        self.assertEqual(response.status_code, 200)

        response = self.client.options(self.accounts_url, format='json')
        self.assertEqual(response.status_code, 200)

    def _check_result_item(self, item, orig_account):
        self.assertEqual(list(sorted(item.keys())), list(sorted(['id', 'owner', 'balance', 'currency'])))
        self.assertEqual(item['id'], orig_account.id)
        self.assertEqual(item['owner'], orig_account.owner)
        self.assertEqual(Decimal(item['balance']), orig_account.balance)
        self.assertEqual(item['currency'], orig_account.currency)

    def test_accounts_api_list(self):
        response = self.client.get(self.accounts_url, format='json')
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(len(result), 4)
        for item, orig_account in zip(result, self.accounts):
            self._check_result_item(item, orig_account)

    def test_accounts_pay_validations(self):
        with self.assertRaises(InvalidAccountCurrency) as cm:
            self.from_account.pay(self.to_account, Decimal(1), CURRENCY_USD)
        the_exception = cm.exception
        self.assertEqual(
            list(sorted(the_exception.account_ids)),
            list(sorted([self.from_account.pk, self.to_account.pk]))
        )

        with self.assertRaises(InvalidAccountCurrency) as cm:
            self.from_account.pay(self.usd_account, Decimal(1), CURRENCY_USD)
        the_exception = cm.exception
        self.assertEqual(the_exception.account_ids, [self.from_account.pk])

        with self.assertRaises(InvalidAmount):
            self.from_account.pay(self.to_account, Decimal(-10), CURRENCY_PHP)

        with self.assertRaises(InsufficientBalance):
            self.empty_account.pay(self.to_account, Decimal(10), CURRENCY_PHP)

    def test_accounts_pay(self):
        self.from_account.pay(self.to_account, Decimal(10), CURRENCY_PHP)

        self.from_account = Account.objects.get(pk=self.from_account.pk)
        self.to_account = Account.objects.get(pk=self.to_account.pk)

        self.assertEqual(self.from_account.balance, Decimal(190))
        self.assertEqual(self.to_account.balance, Decimal(110))
        self.assertEqual(Payment.objects.count(), 2)

        incoming_payment = Payment.objects.get(to_account=self.from_account)
        self.assertEqual(incoming_payment.amount, Decimal(10))
        self.assertEqual(incoming_payment.currency, CURRENCY_PHP)
        self.assertEqual(incoming_payment.from_account, self.to_account)
        self.assertEqual(incoming_payment.direction, PAYMENT_DIRECTIONS_INCOMING)

        outgoing_payment = Payment.objects.get(to_account=self.to_account)
        self.assertEqual(outgoing_payment.amount, Decimal(10))
        self.assertEqual(outgoing_payment.currency, CURRENCY_PHP)
        self.assertEqual(outgoing_payment.from_account, self.from_account)
        self.assertEqual(outgoing_payment.direction, PAYMENT_DIRECTIONS_OUTGOING)
