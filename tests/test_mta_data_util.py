import datetime

from mta_data_util import train_id_to_start_time


def test_train_id_to_start_time():
    assert train_id_to_start_time('095700_R..N') == datetime.time(hour=15, minute=57, second=0)
