import logging
import os
import ynab

logger = logging.getLogger(__name__)


class YnabClient(object):

    _AUTHORIZATION = "Authorization"
    _BEARER = "Bearer"
    _LAST_USED = "last-used"

    def __init__(self):
        token = os.getenv("YNAB_PAT")
        self.config = ynab.Configuration(
            api_key={self._AUTHORIZATION: token},
            api_key_prefix={self._AUTHORIZATION: self._BEARER},
        )
        self.client = ynab.ApiClient(self.config)
        self.monzo_account_name = os.getenv("MONZO_ACCOUNT_NAME")

    def budgets(self):
        budgets = ynab.BudgetsApi(self.client)
        json = budgets.get_budgets()
        logger.info(f"Retrieved YNAB budgets: {json}")
        return json

    def find_monzo_id(self):
        accounts = ynab.AccountsApi(self.client)
        res = accounts.get_accounts(self._LAST_USED)
        for account in res.data.accounts:
            if account.name == self.monzo_account_name:
                monzo_id = account.id
                logger.debug(
                    f"Found ID {monzo_id} for Monzo account {self.monzo_account_name}"
                )
                return monzo_id
        logger.error(
            f"Found no Monzo account with name {self.monzo_account_name} in YNAB"
        )
        return None

    def create_transaction(self, budget_id, data):
        transactions = ynab.TransactionsApi(self.client)
        res = transactions.create_transaction(budget_id, data)
        logger.info(f"Created YNAB transaction {res}")
        return res

    @staticmethod
    def convert_pence_to_milliunits(pence: int):
        return pence * 10
