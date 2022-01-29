from pynab_monzo.ynab import YnabClient
from pynab_monzo.redis import get_redis
import logging
import http

client = YnabClient()
logger = logging.getLogger(__name__)


def translate_monzo_to_ynab(json):
    data = json["data"]
    merchant = data["merchant"]
    account_id = client.find_monzo_id()
    amount = client.convert_pence_to_milliunits(data["amount"])
    date = data["created"].split("T")[0]
    try:
        payee = merchant["name"]
    except TypeError as e:
        logger.warn(f"Monzo transaction {json} threw {e}")
        payee = data["description"]
    return {
        "transaction": {
            "account_id": account_id,
            "amount": amount,
            "date": date,
            "payee_name": payee,
        }
    }


def is_pot_transaction(transaction_description: str) -> bool:
    return transaction_description.startswith("pot_")


def is_monzo_transaction_processed(transaction_id: str) -> bool:
    data_store = get_redis()
    return bool(data_store.exists(transaction_id))


def save_monzo_transaction_id(transaction_id: str) -> bool:
    data_store = get_redis()
    return data_store.set(transaction_id, "", ex=300)


def handle_incoming_transaction(json):
    monzo_transaction_id = json["data"]["id"]
    monzo_transaction_description = json["data"]["description"]

    if is_monzo_transaction_processed(monzo_transaction_id):
        logger.debug(f"Monzo transaction {monzo_transaction_id} is already processed")
        return http.HTTPStatus.OK

    save_monzo_transaction_id(monzo_transaction_id)

    if is_pot_transaction(monzo_transaction_description):
        logger.debug(f"Monzo transaction {monzo_transaction_id} is a pot transaction")
        return http.HTTPStatus.OK

    outgoing_json = translate_monzo_to_ynab(json)
    logger.debug(f"Translated Monzo transaction to: {outgoing_json}")
    client.create_transaction(outgoing_json)

    return http.HTTPStatus.CREATED
