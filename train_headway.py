from collections import namedtuple, OrderedDict
from datetime import datetime

from google.transit import gtfs_realtime_pb2

from tinydb import TinyDB

from mta_data_util import FeedPoller, generate_feed_filter
from util import ExpiringSet, print_with_time

Train = namedtuple('Train', ['id', 'time'])


R_77_N_STOP_NAME = 'R43N'
R_77_N_STOP_NUMBER = 3

PATH_TO_DATA_STORE = 'arrived_trains.json'


class TrainHeadwayFeedProcessor:
    def __init__(self, arrived_train_db):
        self.arrived_trains = OrderedDict()
        # id unique per day, so remove ids after they can be presumed to have finished their run
        self.alerted_trains = ExpiringSet(expiration_seconds=60 * 60 * 4)
        self.arrived_train_db = arrived_train_db

    @staticmethod
    def get_feed_filter():
        return generate_feed_filter(lines='R', directions='N', process_vehicle=True)

    def find_arrived_trains_in_feed(self, feed):
        arrived_trains_in_feed = {}
        for entity in feed:
            vehicle, trip = entity.vehicle, entity.vehicle.trip
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

    def process_feed(self, feed):
        newly_arrived_trains = self.find_arrived_trains_in_feed(feed)
        for train, train_time in newly_arrived_trains.items():
            self.arrived_train_db.insert({'train': train, 'time': train_time.isoformat()})
        self.print_arrived_trains(newly_arrived_trains)


if __name__ == '__main__':
    FeedPoller(TrainHeadwayFeedProcessor(TinyDB(PATH_TO_DATA_STORE))).start()

