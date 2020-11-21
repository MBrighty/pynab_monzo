import pytest
from pynab_monzo.monzo import MonzoClient
import os
import httpretty
import json
import re


@pytest.fixture
def webhook_reponse():
    with open("tests/fixtures/webhook_response.json") as f:
        response = json.load(f)
        yield response


@pytest.mark.integration
def test_monzo_client_can_connect():
    testClient = MonzoClient()
    assert testClient.whoami()["authenticated"] is True


@httpretty.activate
def test_monzo_client_can_register_webhook(webhook_reponse):
    httpretty.register_uri(
        httpretty.POST,
        re.compile("https://api.monzo.com/webhooks/?"),
        json.dumps(webhook_reponse),
    )
    testClient = MonzoClient()
    result = testClient.register_webhook(
        os.getenv("MONZO_ACCOUNT"), "https://www.example.com/test-webhook"
    )
    headers = dict(httpretty.last_request().headers)
    assert result["webhook"]["id"] is not None
    if not headers["Authorization"].startswith("Bearer "):
        assert False, "Authorization header did not have correct form"
