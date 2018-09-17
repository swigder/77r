import glob
import os

from google.protobuf.text_format import Merge
from google.transit import gtfs_realtime_pb2

from read_feed import FeedProcessor

changes = {
    '20180901T112250.proto': {'067853_R..N': '11:21:49'},
    '20180901T113453.proto': {'069050_R..N': '11:33:49'},
    '20180901T114555.proto': {'070150_R..N': '11:44:49'},
    '20180901T120400.proto': {'071888_R..N': '12:02:49'},
    '20180901T121232.proto': {'072806_R..N': '12:11:40'},
    '20180901T122235.proto': {'073850_R..N': '12:21:40'},
}


def test_feed_processor():
    feed_processor = FeedProcessor()

    files = glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'examples', '*.proto'))
    for filepath in sorted(files):
        with open(filepath) as f:
            feed = gtfs_realtime_pb2.FeedMessage()
            Merge(f.read(), feed)
            newly_arrived_trains = feed_processor.find_arrived_trains_in_feed(feed)
            feed_processor.print_arrived_trains(newly_arrived_trains)
            filename = os.path.split(filepath)[1]
            if filename not in changes:
                assert len(newly_arrived_trains) == 0, filename
            else:
                assert len(newly_arrived_trains) == len(changes[filename]), filename
