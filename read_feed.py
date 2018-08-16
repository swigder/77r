import time
from collections import namedtuple
from datetime import datetime

from google.transit import gtfs_realtime_pb2

import urllib.request


Train = namedtuple('Train', ['id', 'time'])


with open('api.key', 'r') as f:
    api_key = f.read()
r_77_northbound = 'R43N'
frequency = 30.0


pending_trains = {}
arrived_trains = []


def print_with_time(*msg):
    print(datetime.now().strftime('%Y-%m-%dT%H:%M:%S'), *msg)


def is_northbound_r_trip(trip):
    return trip.route_id == 'R' and trip.trip_id.endswith('N')


while True:
    try:
        feed = gtfs_realtime_pb2.FeedMessage()
        response = urllib.request.urlopen('http://datamine.mta.info/mta_esi.php?key={}&feed_id=16'.format(api_key))
        feed.ParseFromString(response.read())
        trips_in_feed = {}
        for entity in feed.entity:
            # VehiclePosition type messages let you know where the train actually is. since train id's can change before
            # they leave the terminal (since id's are based on departure time), ignore any trains that haven't started.
            # todo this relies on current behavior of vehicle updates coming after train status updates
            if entity.HasField('vehicle'):
                trip = entity.vehicle.trip
                if is_northbound_r_trip(trip) and entity.vehicle.current_stop_sequence == 0:
                    del trips_in_feed[trip.trip_id]
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
        for key, value in sorted(pending_trains.items(), key=lambda kv: kv[1]):  # order by arrival time ascending
            if key not in trips_in_feed:
                arrived_trains.append(Train(key, value))  # todo technically a race condition though unlikely to be met
                if len(arrived_trains) == 1:  # don't post first train since we don't have headway
                    continue

                most_recent_train_time = arrived_trains[-2].time
                if value < most_recent_train_time:  # todo better handling for order mix-ups
                    print_with_time('Out of order! Train {} at {} before most recent at {}'
                                    .format(key, value, most_recent_train_time))
                    # todo do we want to keep this in list of arrived trains?
                    continue

                print_with_time('Northbound R train {} arrived at 77th St station at {}, {:.2f} minutes after most '
                                'recent train.'.format(key, value, (value-most_recent_train_time).seconds / 60))
        pending_trains = trips_in_feed

    except:  # don't care what happens, sleep and try again - todo maybe be a bit smarter
        pass

    time.sleep(frequency)
