from train_headway import TrainHeadwayFeedProcessor
from .test_feed_poller import TestFeedPoller

expected_results = [
    {'train': '067853_R..N', 'time': '2018-09-01T11:22:29'},
    {'train': '069050_R..N', 'time': '2018-09-01T11:34:24'},
    {'train': '070150_R..N', 'time': '2018-09-01T11:45:40'},
    {'train': '071888_R..N', 'time': '2018-09-01T12:03:25'},
    {'train': '072806_R..N', 'time': '2018-09-01T12:12:00'},
    {'train': '073850_R..N', 'time': '2018-09-01T12:22:00'},
]


def test_feed_processor():
    class MockDb:
        def __init__(self):
            self.data = []

        def insert(self, item):
            print(item)
            self.data.append(item)

    mock_db = MockDb()
    TestFeedPoller(TrainHeadwayFeedProcessor(mock_db)).start()
    print(mock_db.data)
    assert mock_db.data == expected_results
