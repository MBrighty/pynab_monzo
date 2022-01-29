import logging
import os
import requests

logger = logging.getLogger(__name__)


class YnabClient(object):

    _AUTHORIZATION = "Authorization"
    _API_BASE = "https://api.youneedabudget.com/v1/"
    _BEARER = "Bearer"
    _LAST_USED = "last-used"

    def __init__(self):
        token = os.getenv("YNAB_PAT")
        self.monzo_account_name = os.getenv("MONZO_ACCOUNT_NAME")

        self._session = requests.Session()
        self._session.headers[self._AUTHORIZATION] = f"{self._BEARER} {token}"

    def budgets(self):
        budgets = self._session.get(f"{self._API_BASE}budgets")
        json = budgets.json()
        logger.info(f"Retrieved YNAB budgets: {json}")
        return json

    def find_monzo_id(self):
        res = self._session.get(
            f"{self._API_BASE}budgets/{self._LAST_USED}/accounts"
        ).json()
        for account in res["data"]["accounts"]:
            if account["name"] == self.monzo_account_name:
                monzo_id = account["id"]
                logger.debug(
                    f"Found ID {monzo_id} for Monzo account {self.monzo_account_name}"
                )
                return monzo_id
        logger.error(
            f"Found no Monzo account with name {self.monzo_account_name} in YNAB"
        )
        return None

    def create_transaction(self, data):
        res = self._session.post(
            f"{self._API_BASE}budgets/{self._LAST_USED}/transactions", json=data
        )
        logger.info(f"Created YNAB transaction {res}")
        return res

    @staticmethod
    def convert_pence_to_milliunits(pence: int):
        return pence * 10
