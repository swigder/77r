from collections import OrderedDict
from datetime import datetime


class ExpiringSet:
    items = OrderedDict()

    def __init__(self, expiration_seconds):
        self.expiration_seconds = expiration_seconds

    def add(self, item):
        self.items[item] = datetime.now()

    def __contains__(self, item):
        def expired(insert_time):
            return (now - insert_time).seconds > self.expiration_seconds

        now = datetime.now()
        for key, value in list(self.items.items()):
            if expired(value):
                del self.items[key]
            else:
                break  # we're using ordered dict
        return item in self.items
