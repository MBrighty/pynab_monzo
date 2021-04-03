from flask import Flask, request
from pynab_monzo.controllers import webhook
from werkzeug.exceptions import UnsupportedMediaType
import logging
import sys
import os

app = Flask(__name__)
logging.basicConfig(
    stream=sys.stdout,
    format="%(asctime)s - %(name)s - %(levelname)s: %(message)s",
    datefmt="%d %b %Y %H:%M:%S",
    level=os.environ.get("LOG_LEVEL", "DEBUG"),
)
logger = logging.getLogger(__name__)


@app.route("/monzo-hook", methods=["POST"])
def monzo_hook():
    if not request.is_json:
        logger.info(f"Monzo hook called with unsupported mimetype: {request.mimetype}")
        raise UnsupportedMediaType()
    logger.info(f"Monzo hook called with request body: {request.json}")
    status_code = webhook.handle_incoming_transaction(request.json)
    return ("", status_code)
