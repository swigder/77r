from datetime import datetime, timedelta
from time import sleep

from util import ExpiringSet


class TestNowProvider:
    def __init__(self, start=datetime.now()):
        self.time = start

    def increment_seconds(self, seconds):
        self.time += timedelta(seconds=seconds)

    def now(self):
        return self.time


def test_expiring_set():
    now_provider = TestNowProvider()
    expiring_set = ExpiringSet(expiration_seconds=10, now_provider=now_provider)
    assert len(expiring_set.items) == 0
    assert list(expiring_set.items.keys()) == []
    expiring_set.add('a')
    assert len(expiring_set.items) == 1
    assert list(expiring_set.items.keys()) == ['a']
    now_provider.increment_seconds(8)
    expiring_set.add('b')
    assert len(expiring_set.items) == 2
    assert list(expiring_set.items.keys()) == ['a', 'b']
    now_provider.increment_seconds(8)
    assert 'a' not in expiring_set
    assert 'b' in expiring_set
    assert len(expiring_set.items) == 1
    assert list(expiring_set.items.keys()) == ['b']
