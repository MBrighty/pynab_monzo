from pytest import fixture
from pynab_monzo.controllers.webhook import (
    is_monzo_transaction_processed,
    save_monzo_transaction_id,
)
from pynab_monzo.redis import set_redis


@fixture
def cleanup_redis_stub():
    yield
    set_redis(None)


def test_already_processed_transactions_return_true(cleanup_redis_stub):
    class RedisStub(object):
        def exists(self, *names):
            return 1

    # Make this a more realistic ID
    set_redis(RedisStub())
    assert is_monzo_transaction_processed("monzo_transaction_id")


def test_unprocessed_transactions_return_false(cleanup_redis_stub):
    class RedisStub(object):
        def exists(self, *names):
            return 0

    # Make this a more realistic ID
    set_redis(RedisStub())
    assert is_monzo_transaction_processed("monzo_transaction_id") is False


def test_transaction_ids_can_be_saved_to_redis(cleanup_redis_stub):
    class RedisStub(object):
        def set(self, key, value, ex) -> bool:
            return key == "monzo_transaction_id" and value == "" and ex == 300

    # Make this a more realistic ID
    set_redis(RedisStub())
    assert save_monzo_transaction_id("monzo_transaction_id")
