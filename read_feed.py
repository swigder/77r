import time
from collections import namedtuple, OrderedDict
from datetime import datetime

from google.protobuf.message import DecodeError
from google.transit import gtfs_realtime_pb2

from tinydb import TinyDB

from mta_data_util import download_feed, is_northbound_r_trip
from util import ExpiringSet

Train = namedtuple('Train', ['id', 'time'])


R_77_N_STOP_NAME = 'R43N'
R_77_N_STOP_NUMBER = 3

POLL_FREQUENCY = 30.0  # seconds
PATH_TO_DATA_STORE = 'arrived_trains.json'


def print_with_time(*msg):
    print(datetime.now().strftime('%Y-%m-%dT%H:%M:%S'), *msg)


class FeedProcessor:
    arrived_trains = OrderedDict()
    # id unique per day, so remove ids after they can be presumed to have finished their run
    alerted_trains = ExpiringSet(expiration_seconds=60 * 60 * 4)

    def find_arrived_trains_in_feed(self, current_feed):
        arrived_trains_in_feed = {}
        for entity in current_feed.entity:
            # VehiclePosition type messages let you know where the train actually is.
            if entity.HasField('vehicle'):
                vehicle, trip = entity.vehicle, entity.vehicle.trip
                if is_northbound_r_trip(trip):
                    if vehicle.current_stop_sequence == R_77_N_STOP_NUMBER and \
                            vehicle.current_status == gtfs_realtime_pb2.VehiclePosition.STOPPED_AT:
                        if trip.trip_id not in self.arrived_trains:  # resilient against repeat feeds / long dwell times
                            arrived_trains_in_feed[trip.trip_id] = datetime.fromtimestamp(entity.vehicle.timestamp)
                    elif vehicle.current_stop_sequence > R_77_N_STOP_NUMBER and \
                            trip.trip_id not in self.arrived_trains and \
                            trip.trip_id not in self.alerted_trains:
                        print_with_time('Train {} currently at stop {} was never marked as arrived'
                                        .format(trip.trip_id, vehicle.current_stop_sequence))
                        self.alerted_trains.add(trip.trip_id)
            # todo handle short dwell times (i.e., no feed where STOPPED_AT R_77_N_STOP_NUMBER) using former approach
        self.arrived_trains.update(arrived_trains_in_feed)
        return arrived_trains_in_feed

    def print_arrived_trains(self, trains):
        for key, value in sorted(trains.items(), key=lambda kv: kv[1]):  # order by arrival time ascend
            if len(self.arrived_trains) == 1:  # don't have headway for first train
                print_with_time('Northbound R train {} arrived at 77th St station at {}'.format(key, value))
            else:
                previous_arrival = self.arrived_trains[list(self.arrived_trains)[-2]]
                if value < previous_arrival:  # todo better handling for order mix-ups
                    print_with_time('Out of order! Train {} at {} before most recent at {}'
                                    .format(key, value, previous_arrival))
                else:
                    print_with_time('Northbound R train {} arrived at 77th St station at {}, {:.2f} minutes after '
                                    'most recent train.'.format(key, value,
                                                                (value - previous_arrival).seconds / 60))


if __name__ == '__main__':
    with open('api.key', 'r') as f:
        api_key = f.read()

    feed_processor = FeedProcessor()
    arrived_trains_db = TinyDB(PATH_TO_DATA_STORE)

    while True:
        try:
            feed = download_feed(api_key)
            newly_arrived_trains = feed_processor.find_arrived_trains_in_feed(feed)
            for train, train_time in newly_arrived_trains.items():
                arrived_trains_db.insert({'train': train, 'time': train_time.isoformat()})
            feed_processor.print_arrived_trains(newly_arrived_trains)
        except DecodeError as e:
            print_with_time('Decode error!', e)
            # todo print what the actual problem was
        except TimeoutError as e:
            print_with_time('Timeout error!', e)

        time.sleep(POLL_FREQUENCY)

