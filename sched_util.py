"""Utility functions for scheduler"""

# there's a lot of ugly calculation based on dimensions and whatnot, this
# is sorta low-level, other modules should only need:
#
# start_times
# timeslot
# x_time
# y_time
# time_to_str

from draw import Rectangle, Point

class Section:
    """Information about a scheduled section"""
    def __init__(self, day, start, num, ta, end):
        if day in "MTWRF":
            self.day = day
        else:
            raise ValueError("Day must be one of MTWRF")
        self.start = start
        self.num = int(num)
        self.ta = ta
        self.end = end

    def __repr__(self):
        return "Section(%s, %s, %d, %s, %s)" % (self.day, 
                                                time_to_str(self.start),
                                                self.num,
                                                self.ta,
                                                time_to_str(self.end))

start_times = [(7,45),  (8,50),  (9,55), (11,0), (12,5), (13,20),
               (14,25), (15,30), (16,35), (19,5), (21,0), (22,0), (23,0)]

# calculate timespan from start_times (if you need this, uncomment)
#max_time = start_times[-1][0]*60 + start_times[-1][1]
#min_time = start_times[0][0]*60 + start_times[0][1]
#timespan = max_time - min_time # 915 min

# if this changes, comment it and then uncomment the above 3 lines
timespan = 915

def minutes(m, scene):
    """convert from time-based minutes to screen (vert) distance"""
    bg = scene.objects[0]
    return (1.0 * bg.height / timespan) * m

def index_of(item, seq):
    """return index of item (if it exists)"""
    for i in range(len(seq)):
        if seq[i] == item:
            return i

def to_min(time):
    """convert an (hour, minute) tuple to just minutes"""
    h, m = time
    return h*60 + m

def sub_times(t1, t2):
    """subtract t2 from t1, answer in minutes"""
    return to_min(t1) - to_min(t2)

def time_to_str(time):
    h, m = time
    h = h % 12
    if h == 0:
        h = 12
    return "%d:%02d" % (h, m)

def inches(x):
    """Converts to inches (72 pts. == 1 in.)"""
    return 72 * x

def y_time(time, scene):
    """calculate the y position within a schedule of the given time"""
    bg = scene.get_canvas()
    first_period = to_min(start_times[0])
    return bg.max_y - minutes(to_min(time) - first_period, scene)

def x_time(day, scene):
    bg = scene.get_canvas()
    day_width = bg.width / 6.0
    # the "_" is for the label column :)
    return index_of(day, "_MTWRF") * day_width + bg.min_x

def timeslot(sect, scene):
    """Returns a Rectangle positioned at the given day and start time """
    # get "left" and "right" of the day rectangle
    day_width = scene.objects[0].width / 6.0
    xpos_left = x_time(sect.day, scene)
    xpos_right = xpos_left + day_width

    # get "top" and "bottom" of the timeslot rectangle
    ypos_top = y_time(sect.start, scene)
    ypos_bot = y_time(sect.end, scene)

    return Rectangle(Point(xpos_left, ypos_bot),
                     Point(xpos_right, ypos_top))
