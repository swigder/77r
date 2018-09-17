import datetime


def train_id_to_start_time(train_id):
    hundredth_of_minutes_past_midnight = int(train_id.split('_')[0])
    minutes_past_midnight = hundredth_of_minutes_past_midnight // 100
    return datetime.time(hour=minutes_past_midnight // 60, minute=minutes_past_midnight % 60)
