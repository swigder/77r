import time
from datetime import datetime

from google.transit import gtfs_realtime_pb2

# from twisted.internet import task
# from twisted.internet import reactor

import urllib.request

with open('api.key', 'r') as f:
    api_key = f.read()
r_77_northbound = 'R43N'
frequency = 30.0


pending_trips = {}
most_recent_trip = datetime.now()  # todo handle first update


while True:
    feed = gtfs_realtime_pb2.FeedMessage()
    response = urllib.request.urlopen('http://datamine.mta.info/mta_esi.php?key={}&feed_id=16'.format(api_key))
    feed.ParseFromString(response.read())
    trips_in_feed = {}
    for entity in feed.entity:
        trip_update = entity.trip_update
        trip = trip_update.trip
        if trip.route_id == 'R' and trip.trip_id.endswith('N'):
            for stop_time_update in trip_update.stop_time_update:
                if stop_time_update.stop_id == r_77_northbound:
                    trips_in_feed[trip.trip_id] = datetime.fromtimestamp(stop_time_update.arrival.time)
    for key, value in pending_trips.items():
        if key not in trips_in_feed:
            print('{}: Northbound R train {} arrived at 77th St station, {} minutes after most recent train.'
                  .format(value, key, (value-most_recent_trip).seconds / 60))
            most_recent_trip = value  # todo technically a race condition although unlikely to be met
    pending_trips = trips_in_feed
    time.sleep(frequency)


# read_feed_task = task.LoopingCall(read_feed)
# read_feed_task.start(frequency)
#
# reactor.run()
