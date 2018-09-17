from time import sleep

from util import ExpiringSet


def test_fixed_length_set():
    expiring_set = ExpiringSet(expiration_seconds=5)
    assert len(expiring_set.items) == 0
    assert list(expiring_set.items.keys()) == []
    expiring_set.add('a')
    assert len(expiring_set.items) == 1
    assert list(expiring_set.items.keys()) == ['a']
    sleep(2)
    expiring_set.add('b')
    assert len(expiring_set.items) == 2
    assert list(expiring_set.items.keys()) == ['a', 'b']
    sleep(4)
    assert 'a' not in expiring_set
    assert 'b' in expiring_set
    assert len(expiring_set.items) == 1
    assert list(expiring_set.items.keys()) == ['b']
