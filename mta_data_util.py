import datetime
import urllib.request

from google.transit import gtfs_realtime_pb2


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


