from typing import List


class InsufficientBalance(Exception):
    """
    Exception for informing, that account does not have enough money
    """
    pass


class InvalidAccountCurrency(Exception):
    """
    Exception for informing, that account_ids currency is not valid for the operation
    """
    account_ids = None

    def __init__(self, account_ids: List[str]):
        self.account_ids = account_ids


class InvalidAmount(Exception):
    """
    Exception for informing, that amount of money is not valid for the operation
    """
    pass
