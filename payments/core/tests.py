from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from core.const import CURRENCY_PHP
from core.models import Account


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
        )
        Account.objects.bulk_create(self.accounts)

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

    def test_accounts_list(self):
        response = self.client.get(self.accounts_url, format='json')
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(len(result), 3)
        for item, orig_account in zip(result, self.accounts):
            self._check_result_item(item, orig_account)
