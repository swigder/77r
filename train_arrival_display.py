import time
from datetime import datetime

from google.protobuf.message import DecodeError
from google.transit import gtfs_realtime_pb2

from mta_data_util import download_feed, is_northbound_r_trip
from util import print_with_time

R_77_N_STOP_NAME = 'R43N'
R_77_N_STOP_NUMBER = 3

POLL_FREQUENCY = 30.0  # seconds


def get_next_trains(current_feed):
    trips_in_feed = {}
    for entity in current_feed.entity:
        # VehiclePosition type messages let you know where the train actually is.
        if not entity.HasField('trip_update'):
            continue
        trip_update, trip = entity.trip_update, entity.trip_update.trip
        if not is_northbound_r_trip(trip):
            continue
        for stop_time_update in trip_update.stop_time_update:
            if stop_time_update.stop_id == R_77_N_STOP_NAME:
                trips_in_feed[trip.trip_id] = datetime.fromtimestamp(stop_time_update.arrival.time)
    return trips_in_feed


def format_next_trains(next_train_times, max_trains=3):
    now = datetime.now()
    minutes_to_next = sorted([(v-now).seconds // 60 for v in next_train_times.values()])
    return ' - '.join(map(str, minutes_to_next[:max_trains]))


def pad(string, max_len=16):
    padding_length = max(0, (max_len - len(string)) // 2)
    padding = ' ' * padding_length
    return padding + string + padding


if __name__ == '__main__':
    with open('api.key', 'r') as f:
        api_key = f.read()

    while True:
        try:
            feed = download_feed(api_key)
            print(pad(datetime.now().strftime('%H:%M') + ' Next R'))
            print(pad(format_next_trains(get_next_trains(feed)) + ' mins'))
            print()
        except DecodeError as e:
            print_with_time('Decode error!', e)
            # todo print what the actual problem was
        except TimeoutError as e:
            print_with_time('Timeout error!', e)

        time.sleep(POLL_FREQUENCY)

