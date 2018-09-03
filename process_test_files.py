import glob
from datetime import datetime
import os

from google.protobuf.text_format import Merge
from google.transit import gtfs_realtime_pb2

EXAMPLE_DIR = '/Users/xx/Documents/source/77r/examples'
r_77_northbound = 'R43N'


def is_northbound_r_trip(trip):
    return trip.route_id == 'R' and trip.trip_id.endswith('N')


files = glob.glob(os.path.join(EXAMPLE_DIR, '*.proto'))
for filename in sorted(files):
    print(filename)
    with open(os.path.join(EXAMPLE_DIR, filename), 'rb') as f:
        feed = gtfs_realtime_pb2.FeedMessage()
        Merge(f.read(), feed)
        for entity in feed.entity:
            if entity.HasField('trip_update'):
                trip_update = entity.trip_update
                trip = trip_update.trip
                if is_northbound_r_trip(trip):
                    for stop_time_update in trip_update.stop_time_update:
                        if stop_time_update.stop_id == r_77_northbound:
                            print(trip.trip_id, datetime.fromtimestamp(stop_time_update.arrival.time))



