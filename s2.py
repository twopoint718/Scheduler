import sys
from draw import HLine, Point, Rectangle, Scene, VLine
from sched_parser import parse_all, parse_file

def inches(x):
    """Converts to inches (72 pts. == 1 in.)"""
    return 72 * x

def schedule_grid(title, scene):
    """Draws a standard Schedule grid:

    |       | Mon | Tue | Wed | Thur | Fri |
    |-------+-----+-----+-----+------+-----|
    |  7:45 |     |     |     |      |     |
    |  8:50 |     |     |     |      |     |
    |  9:55 |     |     |     |      |     |
    | 11:00 |     |     |     |      |     |
    | 12:05 |     |     |     |      |     |
    |  1:20 |     |     |     |      |     |
    |  2:25 |     |     |     |      |     |
    | ...   |     |     |     |      |     |

    """
    margin = 5
    
    # add background (shaded area)
    o, e = scene.bounds.corners()
    bg = Rectangle(o, e)
    bg = bg.shrink(margin)\
        .lower(30)\
        .fill(0.8)\
        .label_above(title, 18, 8) # fontsize 18, move up 8pt

    day_width = bg.width / 6.0

    # label column on left
    lab = Rectangle(bg.origin.copy(), Point(bg.min_x + day_width, bg.max_y))

    # add days
    adjustment = -2 # move labels slightly down
    mon = lab.copy().translate((day_width, 0)).label_above("Monday", 12, adjustment)
    tue = mon.copy().translate((day_width, 0)).label_above("Tuesday", 12, adjustment)
    wed = tue.copy().translate((day_width, 0)).label_above("Wednesday", 12, adjustment)
    thu = wed.copy().translate((day_width, 0)).label_above("Thursday", 12, adjustment)
    fri = thu.copy().translate((day_width, 0)).label_above("Friday", 12, adjustment)

    # add the days to the scene
    scene.add(bg)
    scene.add(mon)
    scene.add(tue)
    scene.add(wed)
    scene.add(thu)
    scene.add(fri)

    # label timeslots
    start_times = [(7,45),  (8,50),  (9,55), (11,0), (12,5), (13,20),
                   (14,25), (15,30), (16,35), (19,5), (21,0), (22,0), (23,0)]

    max_time = start_times[-1][0]*60 + start_times[-1][1]
    min_time = start_times[0][0]*60 + start_times[0][1]
    min_span = max_time - min_time # 915 min

    # convert minutes to screen dimensions (no offsets)
    minutes = lambda m: (1.0 * bg.height / min_span) * m

    # subtract a later time from an earlier one
    diff_time = lambda t1, t2: (t2[0]*60 + t2[1]) - (t1[0]*60 + t1[1])

    diff_times = list(map(diff_time, start_times, start_times[1:]))
    diff_times.insert(0, 0)

    # fill in the time labels (and horiz lines)
    width = bg.max_x - bg.min_x
    for i in range(1, len(diff_times)):
        line = HLine(Point(bg.min_x, bg.max_y - minutes(sum(diff_times[:i]))), width)
        h = start_times[i-1][0] % 12
        if h == 0:
            h = 12
        m = start_times[i-1][1]
        line.label_below_left("%d:%02d" % (h, m), 8, 5, -8)
        scene.add(line)

    return scene

def main():
    paper_size = Point(inches(8.5), inches(4))
    bounding_box = Rectangle(Point(0, 0), paper_size)
    s = Scene(bounding_box)

    # draw the scheduling grid
    s = schedule_grid("Testing", s)
    s.render()

if __name__ == "__main__":
    main()
