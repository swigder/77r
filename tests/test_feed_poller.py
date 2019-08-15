import glob
import os

from google.protobuf.text_format import Merge
from google.transit import gtfs_realtime_pb2


class TestFeedPoller:
    def __init__(self, feed_processor):
        self.feed_processor = feed_processor
        self.feed_filter = self.feed_processor.get_feed_filter()

    def start(self):
        files = glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'examples', '*.proto'))
        for filepath in sorted(files):
            with open(filepath) as f:
                feed = gtfs_realtime_pb2.FeedMessage()
                Merge(f.read(), feed)
                self.feed_processor.process_feed(self.feed_filter.filterTume(feed))
