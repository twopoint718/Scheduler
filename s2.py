import sys
from draw import HLine, Point, Rectangle, Scene, VLine
from sched_parser import parse_all, parse_file

def inches(x):
    return 72 * x

def main():
    bounding_box = Rectangle(Point(0, 0), Point(inches(8.5), inches(4)))
    s = Scene(bounding_box)
    s = schedule_grid(s)
    s.render()

def schedule_grid(scene):
    margin = 5


    
    # add background (shaded area)
    o, e = scene.bounds.origin, scene.bounds.extent
    bg = Rectangle(o, e)
    bg = bg.shrink(margin)\
        .lower(30)\
        .fill(0.8)\
        .label_above("Schedule", 18)

    day_width = bg.width / 6.0

    # label column on left
    lab = Rectangle(bg.origin.copy(), Point(bg.min_x + day_width, bg.max_y))

    # add days
    mon = lab.copy_geom().translate((day_width, 0)).label_above("Monday")
    tue = mon.copy_geom().translate((day_width, 0)).label_above("Tuesday")
    wed = tue.copy_geom().translate((day_width, 0)).label_above("Wednesday")
    thu = wed.copy_geom().translate((day_width, 0)).label_above("Thursday")
    fri = thu.copy_geom().translate((day_width, 0)).label_above("Friday")

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

    # fill in the time labels
    x1, x2 = lab.min_x, lab.max_x
    offset = lab.min_y
    lower = offset + minutes(diff_times[0])
    upper = lower + minutes(diff_times[1])
    for i in range(1, len(diff_times)):
        upper = lower + minutes(diff_times[i])
        p1 = Point(x1, lower)
        p2 = Point(x2, upper)
        r = Rectangle(p1, p2)
        r.label_inside("%d:%02d" % (start_times[i-1][0]%12, start_times[i-1][1]))
        scene.add(r)
        lower = upper

    return scene

if __name__ == "__main__":
    main()
