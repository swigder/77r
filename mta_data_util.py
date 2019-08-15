import datetime
import time
import urllib.request
from urllib.error import URLError

from google.protobuf.message import DecodeError
from google.transit import gtfs_realtime_pb2

from util import print_with_time, split_keys

DEFAULT_POLL_FREQUENCY = 30.0  # seconds - feed is updated this often


TRAIN_LINE_TO_FEED_ID = split_keys({
    '123456S': 1,
    'ACEH': 26,
    'NQRW': 16,
    'BDFM': 21,
    'L': 2,
    'I': 11,  # SIR
    'G': 31,
    'JZ': 36,
    '7': 51
})

FEED_IDS = set(TRAIN_LINE_TO_FEED_ID.values())

FEED_FORMAT = 'http://datamine.mta.info/mta_esi.php?key={}&feed_id={}'


def train_id_to_start_time(train_id):
    hundredth_of_minutes_past_midnight = int(train_id.split('_')[0])
    minutes_past_midnight = hundredth_of_minutes_past_midnight // 100
    return datetime.time(hour=minutes_past_midnight // 60, minute=minutes_past_midnight % 60)


def download_raw_feed(api_key, feed_id):
    response = urllib.request.urlopen(FEED_FORMAT.format(api_key, feed_id))
    return response.read()


def download_feed_by_id(api_key, feed_id):
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(download_raw_feed(api_key, feed_id))
    return feed


def download_feed(api_key, line):
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(download_raw_feed(api_key, TRAIN_LINE_TO_FEED_ID[line]))
    return feed


class FeedFilter:
    def __init__(self, lines, directions, process_vehicle=False, process_trip_update=False):
        self.lines = lines
        self.directions = directions
        self.process_vehicle = process_vehicle
        self.process_trip_update = process_trip_update

    def entity_passes_filter(self, entity):
        if self.process_vehicle and entity.HasField('vehicle'):
            trip = entity.vehicle.trip
        elif self.process_trip_update and entity.HasField('trip_update'):
            trip = entity.trip_update.trip
        else:
            return False
        return trip.route_id in self.lines and trip.trip_id[-1] in self.directions

    def filter(self, feed):
        for entity in feed.entity:
            if self.entity_passes_filter(entity):
                yield entity


class FeedPoller:
    def __init__(self, feed_processor, poll_frequency=DEFAULT_POLL_FREQUENCY):
        self.feed_processor = feed_processor
        self.poll_frequency = poll_frequency
        self.feed_filter = self.feed_processor.get_feed_filter()

    def start(self):
        with open('api.key', 'r') as f:
            api_key = f.read()

        while True:
            try:
                feed = download_feed(api_key, self.feed_filter.lines[0])  # todo handle multiple lines
                feed = self.feed_filter.filter(feed)
                self.feed_processor.process_feed(feed)
            except DecodeError as e:
                print_with_time('Decode error!', e)
                # todo print what the actual problem was
            except TimeoutError as e:
                print_with_time('Timeout error!', e)
            except URLError as e:
                print_with_time('URLError error!', e)

            time.sleep(self.poll_frequency)


