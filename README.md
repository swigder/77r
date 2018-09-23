# 77r

A collection of little tools for studying and coping with the infrequent and frequently delayed service on the R line in Bay Ridge. All scripts are configured to use the 77th Street station as their starting point.

Tools will include:
* `eight_minutes.py`, which studies how travel time for a fixed route varies depending on the trip start time. Anecdotal observation showed that trips to W4 starting at 08:49 took 20 minutes longer than trips starting at 08:41; this script attempts to determine if this is a trend or merely coincidence.
* `train_arrival_display.py`, which displays the arrival time of the next 3 trains, intended for use with a 16x2 display.
* `train_headway.py`, which studies how frequently the train actually arrives and computes daily and weekly stats such as average, minimum, and maximum intervals between trains.
