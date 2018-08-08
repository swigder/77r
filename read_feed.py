from datetime import datetime

from google.transit import gtfs_realtime_pb2
import urllib.request

with open('api.key', 'r') as f:
    api_key = f.read()
r_77_northbound = 'R43N'

feed = gtfs_realtime_pb2.FeedMessage()
response = urllib.request.urlopen('http://datamine.mta.info/mta_esi.php?key={}&feed_id=16'.format(api_key))
feed.ParseFromString(response.read())
for entity in feed.entity:
    trip_update = entity.trip_update
    trip = trip_update.trip
    if trip.route_id == 'R' and trip.trip_id.endswith('N'):
        for stop_time_update in trip_update.stop_time_update:
            if stop_time_update.stop_id == r_77_northbound:
                print(trip.trip_id)
                print(datetime.fromtimestamp(stop_time_update.arrival.time))
