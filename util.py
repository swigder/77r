from collections import OrderedDict
from datetime import datetime


class ExpiringSet:
    def __init__(self, expiration_seconds, now_provider=datetime):
        self.expiration_seconds = expiration_seconds
        self.now_provider = now_provider
        self.items = OrderedDict()

    def add(self, item):
        self.items[item] = self.now_provider.now()

    def __contains__(self, item):
        def expired(insert_time):
            return (now - insert_time).seconds > self.expiration_seconds

        now = self.now_provider.now()
        for key, value in list(self.items.items()):
            if expired(value):
                del self.items[key]
            else:
                break  # we're using ordered dict
        return item in self.items


def split_keys(m_in):
    m_out = {}
    for k, v in m_in.items():
        for i in k:
            m_out[i] = v
    return m_out


def print_with_time(*msg):
    print(datetime.now().strftime('%Y-%m-%dT%H:%M:%S'), *msg)

