import logging
import os
import requests

logger = logging.getLogger(__name__)


class MonzoClientError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MonzoClient(object):

    _HTTPS = "https://"
    _BASE_URL = "api.monzo.com/"
    _WHOAMI = "ping/whoami/"
    _REGISTER_WEBHOOK = "webhooks/"
    _AUTHORIZATION = "Authorization"
    _BEARER = "Bearer"

    def __init__(self):
        self._access_token = os.getenv("MONZO_TOKEN")

    def _create_headers(self):
        return {self._AUTHORIZATION: f"{self._BEARER} {self._access_token}"}

    @classmethod
    def _create_request_url(cls, suffix):
        return f"{cls._HTTPS}{cls._BASE_URL}{suffix}"

    def whoami(self):
        req_url = self._create_request_url(self._WHOAMI)
        headers = self._create_headers()
        response = requests.get(req_url, headers=headers)
        if response.status_code != 200:
            raise MonzoClientError(
                f"whoami returned " f"{response.status_code}: {response.reason}"
            )
        json = response.json()
        logger.info(f"whoami returned: {json}")
        return json

    def register_webhook(self, account_id, url):
        req_url = self._create_request_url(self._REGISTER_WEBHOOK)
        headers = self._create_headers()
        data = {"account_id": account_id, "url": url}
        response = requests.post(req_url, headers=headers, data=data)
        if response.status_code != 200:
            raise MonzoClientError(
                f"Register webook returned "
                f"{response.status_code}: {response.reason}"
            )
        json = response.json()
        logger.info(f"Registered webhook: {json}")
        return json
