from datetime import datetime

from mta_data_util import FeedPoller, FeedFilter

R_77_N_STOP_NAME = 'R43N'
R_77_N_STOP_NUMBER = 3


def format_next_trains(next_train_times, max_trains=3):
    now = datetime.now()
    minutes_to_next = sorted([(v - now).seconds // 60 for v in next_train_times.values()])
    return ' - '.join(map(str, minutes_to_next[:max_trains]))


def pad(string, max_len=16):
    padding_length = max(0, (max_len - len(string)) // 2)
    padding = ' ' * padding_length
    return padding + string + padding


class TrainArrivalDisplayFeedProcessor:
    @staticmethod
    def get_feed_filter():
        return FeedFilter(lines='R', directions='N', process_trip_update=True)

    @staticmethod
    def get_next_trains(feed):
        trips_in_feed = {}
        for entity in feed:
            trip_update, trip = entity.trip_update, entity.trip_update.trip
            for stop_time_update in trip_update.stop_time_update:
                if stop_time_update.stop_id == R_77_N_STOP_NAME:
                    trips_in_feed[trip.trip_id] = datetime.fromtimestamp(stop_time_update.arrival.time)
        return trips_in_feed

    def process_feed(self, feed):
        print(pad(datetime.now().strftime('%H:%M') + ' Next R'))
        print(pad(format_next_trains(self.get_next_trains(feed)) + ' mins'))
        print()


if __name__ == '__main__':
    FeedPoller(TrainArrivalDisplayFeedProcessor()).start()

