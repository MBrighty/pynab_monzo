import random

from pytest import mark

from pynab_monzo.ynab import YnabClient


@mark.integration
def test_ynab_client_can_connect():
    testClient = YnabClient()
    assert testClient.budgets().data is not None


def test_ynab_client_can_convert_positive_amounts_to_milliunits():
    amount = random.randint(1, 10000)  # A credit of 1p - £100
    assert YnabClient.convert_pence_to_milliunits(amount) == amount * 10


def test_ynab_client_can_convert_negative_amounts_to_milliunits():
    amount = -random.randint(1, 10000)  # A debit of 1p - £100
    assert YnabClient.convert_pence_to_milliunits(amount) == amount * 10
