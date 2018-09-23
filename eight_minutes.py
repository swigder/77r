from datetime import datetime

from google.transit import gtfs_realtime_pb2

from mta_data_util import FeedPoller, FeedFilter
from util import print_with_time

R_77_N_STOP_NUMBER = 3
R_36_N_STOP_NUMBER = 8


class EightMinutes:
    def __init__(self):
        self.trains = {}

    def get_feed_filter(self):
        return FeedFilter(lines='R', directions='N', process_vehicle=True)

    def process_feed(self, feed):
        for entity in feed:
            vehicle, trip_id = entity.vehicle, entity.vehicle.trip.trip_id
            if vehicle.current_status == gtfs_realtime_pb2.VehiclePosition.STOPPED_AT:
                if vehicle.current_stop_sequence == R_77_N_STOP_NUMBER:
                    if trip_id not in self.trains:  # resilient against repeat feeds / long dwell times
                        self.trains[trip_id] = datetime.fromtimestamp(entity.vehicle.timestamp)
                elif vehicle.current_stop_sequence == R_36_N_STOP_NUMBER:
                    if trip_id in self.trains:
                        arrival_time = datetime.fromtimestamp(entity.vehicle.timestamp)
                        departure_time = self.trains[trip_id]
                        print_with_time("Train {}: 77 at {}, 36 at {}, trip time {:.2f} minutes".format(
                            trip_id, departure_time, arrival_time, (arrival_time - departure_time).seconds / 60))
                        del self.trains[trip_id]
            # todo handle short dwell times (i.e., no feed where STOPPED_AT R_77_N_STOP_NUMBER)


if __name__ == '__main__':
    FeedPoller(EightMinutes()).start()

