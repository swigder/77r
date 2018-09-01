import time
from collections import namedtuple, OrderedDict
from datetime import datetime

from google.protobuf.message import DecodeError
from google.transit import gtfs_realtime_pb2

import urllib.request


Train = namedtuple('Train', ['id', 'time'])


r_77_northbound = 'R43N'
frequency = 30.0


def print_with_time(*msg):
    print(datetime.now().strftime('%Y-%m-%dT%H:%M:%S'), *msg)


def is_northbound_r_trip(trip):
    return trip.route_id == 'R' and trip.trip_id.endswith('N')


class FeedProcessor:
    pending_trains = {}
    arrived_trains = OrderedDict()

    def process_feed(self, feed):
        trips_in_feed = {}
        trips_to_delete = set()
        for entity in feed.entity:
            # VehiclePosition type messages let you know where the train actually is. since train id's can change before
            # they leave the terminal (since id's are based on departure time), ignore any trains that haven't started.
            if entity.HasField('vehicle'):
                trip = entity.vehicle.trip
                if is_northbound_r_trip(trip) and entity.vehicle.current_stop_sequence == 0:
                    trips_to_delete.add(trip.trip_id)
            # TripUpdate type messages give estimated arrival times for future stops on a given train.
            elif entity.HasField('trip_update'):
                trip_update = entity.trip_update
                trip = trip_update.trip
                if is_northbound_r_trip(trip):
                    for stop_time_update in trip_update.stop_time_update:
                        if stop_time_update.stop_id == r_77_northbound:
                            trips_in_feed[trip.trip_id] = datetime.fromtimestamp(stop_time_update.arrival.time)
            else:
                print_with_time('Unknown entity!', entity)
        for trip_id in trips_to_delete:
            if trip_id in trips_in_feed:
                del trips_in_feed[trip_id]
        for key, value in sorted(self.pending_trains.items(), key=lambda kv: kv[1]):  # order by arrival time ascending
            if key not in trips_in_feed:
                if len(self.arrived_trains) == 0:  # don't have headway for first train
                    print_with_time('Northbound R train {} arrived at 77th St station at {}'.format(key, value))
                else:
                    previous_arrival = self.arrived_trains[next(reversed(self.arrived_trains))]
                    if key in self.arrived_trains:  # train info got updated after we thought it left the station
                        print_with_time('Train {} arrival time updated from {} to {}'
                                        .format(key, self.arrived_trains[key], value))
                    elif value < previous_arrival:  # todo better handling for order mix-ups
                        print_with_time('Out of order! Train {} at {} before most recent at {}'
                                        .format(key, value, previous_arrival))
                    else:
                        print_with_time('Northbound R train {} arrived at 77th St station at {}, {:.2f} minutes after '
                                        'most recent train.'.format(key, value,
                                                                    (value - previous_arrival).seconds / 60))
                self.arrived_trains[key] = value
        self.pending_trains = trips_in_feed


if __name__ == '__main__':
    with open('api.key', 'r') as f:
        api_key = f.read()

    feed_processor = FeedProcessor()

    while True:
        try:
            feed = gtfs_realtime_pb2.FeedMessage()
            response = urllib.request.urlopen('http://datamine.mta.info/mta_esi.php?key={}&feed_id=16'.format(api_key))
            feed.ParseFromString(response.read())
            feed_processor.process_feed(feed)
        except DecodeError as e:
            print_with_time('Decode error!', e)
            # todo print what the actual problem was
        except TimeoutError as e:
            print_with_time('Timeout error!', e)

        time.sleep(frequency)

