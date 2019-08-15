import errno
import sys
import time
from datetime import datetime
from os import path, mkdir
from urllib.error import URLError

from mta_data_util import download_raw_feed, print_with_time, DEFAULT_POLL_FREQUENCY, FEED_IDS


def poll_and_store(output_dir):
    with open('api.key', 'r') as f:
        api_key = f.read()

    for feed_id in FEED_IDS:
        feed_path = path.join(output_dir, str(feed_id))
        try:
            mkdir(feed_path)
        except OSError as e:
            if e.errno == errno.EEXIST and path.isdir(feed_path):
                pass
            else:
                raise

    while True:
        try:
            for feed_id in FEED_IDS:
                print_with_time('Getting feed', feed_id)
                output_file = path.join(output_dir, str(feed_id), '{}_{}.txt'.format(
                    feed_id, datetime.now().strftime('%Y%m%dT%H%M%S')))
                with open(output_file, 'wb') as f:
                    f.write(download_raw_feed(api_key, feed_id))
        except TimeoutError as e:
            print_with_time('Timeout error!', e)
        except URLError as e:
            print_with_time('URLError error!', e)

        time.sleep(DEFAULT_POLL_FREQUENCY)


if __name__ == '__main__':
    poll_and_store(sys.argv[1])
