"""Scheduler is a python script that creates Instructional Lab Schedules
from a set of text files. By default, the program creates a summary page
that has a 12-up view of all the schedules, and detail pages (8.5" x 5")
for each of the individual schedules. These are designed to be suitable for
labeling the lab rooms (please print these on green cardstock).

The input is a set of config files (one per course-room pair).  It should
be named like:

'103_4320.txt'

and have contents like:

M,12:05 301     Ojalvo    14:00
M,14:25 302     Carmody   16:20
M,16:35 303     Ojalvo    18:30
M,19:05 304     N/A       21:00

T,7:45  305     Carmody    9:40
T,9:55  306     Zeng      11:50
T,12:05 307     Zeng      14:00
...

Those fields are:

<day of week>,<start time> <section> <TA name> <end time>

Times are in 24-hour format (but are displayed in 12-hour).

In labs where section number conflicts would occur, a parenthetical mention
of the course number resolves the ambiguity:

T,14:25 (321)301        Dhorkah         17:25
T,19:00 (321)302        Dhorkah         22:00

W,14:25 (623)301        McDermott       17:25
W,19:00 (623)303        McDermott       22:00



"""
__name__ = "Scheduler"
__author__ = "Chris Wilson"
__copyright__ = "Copyright 2011"
__date__ = "2011-06-29"
__license__ = "GPLv3"
__version__ = "0.5"
__maintainer__ = "Chris Wilson"
__email__ = "cwilson@physics.wisc.edu"
__status__ = "Development"
