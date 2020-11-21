from pytest import fixture, mark
from pynab_monzo import app
from pynab_monzo.redis import set_redis
import logging
import json
import re
import httpretty

logger = logging.getLogger(__name__)


@fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


@fixture
def incoming_json():
    with open("tests/fixtures/incoming_transaction.json") as f:
        transaction_json = json.load(f)
        yield json.dumps(transaction_json)


@fixture
def accounts_response():
    with open("tests/fixtures/ynab_get_accounts_response.json") as f:
        accounts_response = json.load(f)
        yield json.dumps(accounts_response)


@fixture
def ynab_request():
    with open("tests/fixtures/ynab_outgoing.json") as f:
        ynab_outgoing = json.load(f)
        yield json.dumps(ynab_outgoing)


@fixture
def ynab_response():
    with open("tests/fixtures/ynab_transaction_response.json") as f:
        ynab_json = json.load(f)
        yield json.dumps(ynab_json)


@fixture
def redis_stub():
    class RedisStub(object):
        def exists(self, *names):
            return 0

        def set(self, key, value, ex) -> bool:
            return key == "monzo_transaction_id" and value == "" and ex == 300

    redis = RedisStub()
    set_redis(redis)
    yield
    set_redis(None)


@fixture
def redis_exists_stub():
    class RedisStub(object):
        def exists(self, *names):
            return 1

        def set(self, key, value, ex) -> bool:
            return key == "monzo_transaction_id" and value == "" and ex == 300

    redis = RedisStub()
    set_redis(redis)
    yield
    set_redis(None)


@fixture(autouse=True)
def cleanup():
    yield
    if httpretty.is_enabled():
        httpretty.reset()


@mark.integration
@httpretty.activate
def test_sends_ynab_formatted_json_on_monzo_transaction(
    accounts_response, client, redis_stub, incoming_json, ynab_request, ynab_response
):
    def request_callback(request, uri, response_headers):
        assert request.parsed_body["transaction"]["account_id"] == "id-two"
        assert request.parsed_body["transaction"]["amount"] == -3500
        assert request.parsed_body["transaction"]["date"] == "2015-09-04"
        assert (
            request.parsed_body["transaction"]["payee_name"]
            == "The De Beauvoir Deli Co."
        )
        return [201, response_headers, ynab_response]

    httpretty.register_uri(
        httpretty.GET,
        re.compile("https://api.youneedabudget.com/v1/budgets/last-used/accounts/?"),
        accounts_response,
    )
    httpretty.register_uri(
        httpretty.POST,
        re.compile(
            "https://api.youneedabudget.com/v1/budgets/last-used/transactions/?"
        ),
        body=request_callback,
    )
    response = client.post(
        "/monzo-hook", content_type="application/json", data=incoming_json
    )
    assert response.status_code == 201


@mark.integration
@httpretty.activate
def test_monzo_webhook_handles_duplicate_transactions(
    accounts_response, client, redis_exists_stub, incoming_json
):
    httpretty.register_uri(
        httpretty.GET,
        re.compile("https://api.youneedabudget.com/v1/budgets/last-used/accounts/?"),
        accounts_response,
    )
    response = client.post(
        "/monzo-hook", content_type="application/json", data=incoming_json
    )
    assert response.status_code == 200


def test_monzo_webhook_returns_error_on_wrong_mime_type(client):
    response = client.post("/monzo-hook", content_type="text/plain")
    assert response.status_code != 200
    assert response.status_code == 415
