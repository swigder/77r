import datetime
import time
import urllib.request

from google.protobuf.message import DecodeError
from google.transit import gtfs_realtime_pb2

from util import print_with_time

DEFAULT_POLL_FREQUENCY = 30.0  # seconds - feed is updated this often


def is_northbound_r_trip(trip):
    return trip.route_id == 'R' and trip.trip_id.endswith('N')


def train_id_to_start_time(train_id):
    hundredth_of_minutes_past_midnight = int(train_id.split('_')[0])
    minutes_past_midnight = hundredth_of_minutes_past_midnight // 100
    return datetime.time(hour=minutes_past_midnight // 60, minute=minutes_past_midnight % 60)


def download_feed(api_key):
    feed = gtfs_realtime_pb2.FeedMessage()
    response = urllib.request.urlopen('http://datamine.mta.info/mta_esi.php?key={}&feed_id=16'.format(api_key))
    feed.ParseFromString(response.read())
    return feed


def generate_feed_filter(lines, directions, process_vehicle=False, process_trip_update=False):
    def trip_passes_filter(trip):
        return trip.route_id in lines and trip.trip_id[-1] in directions

    def feed_generator(feed):
        for entity in feed.entity:
            if process_vehicle and entity.HasField('vehicle') and trip_passes_filter(entity.vehicle.trip):
                yield entity
            elif process_trip_update and entity.HasField('trip_update') and trip_passes_filter(entity.trip_update.trip):
                yield entity
    return feed_generator


class FeedPoller:
    def __init__(self, process_feed_fn, feed_filter=lambda x: x, poll_frequency=DEFAULT_POLL_FREQUENCY):
        self.process_feed_fn = process_feed_fn
        self.feed_filter = feed_filter
        self.poll_frequency = poll_frequency

    def start(self):
        with open('api.key', 'r') as f:
            api_key = f.read()

        while True:
            try:
                feed = download_feed(api_key)
                self.process_feed_fn(self.feed_filter(feed))
            except DecodeError as e:
                print_with_time('Decode error!', e)
                # todo print what the actual problem was
            except TimeoutError as e:
                print_with_time('Timeout error!', e)

            time.sleep(self.poll_frequency)


