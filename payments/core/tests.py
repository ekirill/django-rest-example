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


class PaymentsTestCase(TestCase):
    payments_url = '/v1/payments'

    def setUp(self):
        self.client = APIClient()

        self.owner_1 = 'owner_1'
        self.owner_2 = 'owner_2'

        self.accounts = (
            Account(id='acc_1', owner=self.owner_1, balance=0, currency=CURRENCY_PHP),
            Account(id='acc_2', owner=self.owner_2, balance=200, currency=CURRENCY_PHP),
        )
        Account.objects.bulk_create(self.accounts)

        self.accounts[1].pay(self.accounts[0], Decimal(50), CURRENCY_PHP)
        self.payments = list(Payment.objects.all())

        self.creation_data_json = {
            'from_account': self.accounts[1].pk,
            'to_account': self.accounts[0].pk,
            'amount': '1.5005',
            'currency': CURRENCY_PHP,
        }

    def test_payments_list_methods(self):
        response = self.client.put(self.payments_url, format='json')
        self.assertEqual(response.status_code, 405)

        response = self.client.patch(self.payments_url, format='json')
        self.assertEqual(response.status_code, 405)

        response = self.client.delete(self.payments_url, format='json')
        self.assertEqual(response.status_code, 405)

        response = self.client.get(self.payments_url, format='json')
        self.assertEqual(response.status_code, 200)

        response = self.client.options(self.payments_url, format='json')
        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.payments_url, data=self.creation_data_json, format='json')
        self.assertEqual(response.status_code, 201)

    def _check_result_item(self, item, orig_payment):
        self.assertEqual(
            list(sorted(item.keys())),
            list(sorted(['to_account', 'from_account', 'direction', 'amount', 'currency']))
        )
        self.assertEqual(item['to_account'], orig_payment.to_account.pk)
        self.assertEqual(item['from_account'], orig_payment.from_account.pk)
        self.assertEqual(item['direction'], orig_payment.direction)
        self.assertEqual(Decimal(item['amount']), orig_payment.amount)
        self.assertEqual(item['currency'], orig_payment.currency)

    def test_payments_api_list(self):
        response = self.client.get(self.payments_url, format='json')
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(len(result), 2)
        for item, orig_payment in zip(result, self.payments):
            self._check_result_item(item, orig_payment)

    def test_payment_creation_api(self):
        response = self.client.post(self.payments_url, data=self.creation_data_json, format='json')
        result = response.json()
        self.assertEqual(result, {'status': 'CREATED'})

        # 2 payments were created at setUp
        self.assertEqual(Payment.objects.count(), 4)

        outgoing_payment = Payment.objects.filter(
            from_account__pk=self.creation_data_json['from_account'],
        ).first()  # default ordering is desc
        self.assertEqual(outgoing_payment.to_account_id, self.creation_data_json['to_account'])
        self.assertEqual(outgoing_payment.from_account_id, self.creation_data_json['from_account'])
        self.assertEqual(outgoing_payment.direction, PAYMENT_DIRECTIONS_OUTGOING)
        self.assertEqual(outgoing_payment.amount, Decimal(self.creation_data_json['amount']))
        self.assertEqual(outgoing_payment.currency, self.creation_data_json['currency'])

        incoming_payment = Payment.objects.filter(
            from_account__pk=self.creation_data_json['to_account'],
        ).first()  # default ordering is desc
        self.assertEqual(incoming_payment.to_account_id, self.creation_data_json['from_account'])
        self.assertEqual(incoming_payment.from_account_id, self.creation_data_json['to_account'])
        self.assertEqual(incoming_payment.direction, PAYMENT_DIRECTIONS_INCOMING)
        self.assertEqual(incoming_payment.amount, Decimal(self.creation_data_json['amount']))
        self.assertEqual(incoming_payment.currency, self.creation_data_json['currency'])

        self.assertEqual(outgoing_payment.to_account.balance, Decimal('51.5005'))
        self.assertEqual(outgoing_payment.from_account.balance, Decimal('148.4995'))
