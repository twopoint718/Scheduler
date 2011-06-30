import sys
from draw import HLine, Point, Rectangle, Scene, VLine
from sched_parser import parse_all, parse_file
from sched_util import inches, start_times, timeslot, x_time, y_time, \
                       time_to_str, Section

def schedule_grid(title, scene):
    """Draws a standard Schedule grid:
    """
    margin = 5

    # add background (shaded area)
    o, e = scene.bounds.corners()
    bg = Rectangle(o, e)
    bg = bg.shrink(margin).lower(30).fill(0.8).label_above(title, 18, 6)

    day_width = bg.width / 6.0

    # label column on left
    lab = Rectangle(bg.origin.copy(), Point(bg.min_x + day_width, bg.max_y))

    # add days
    adj = -2 # move labels slightly down
    mon = lab.copy().translate((day_width, 0)).label_above("Monday", 10, adj)
    tue = mon.copy().translate((day_width, 0)).label_above("Tuesday", 10, adj)
    wed = tue.copy().translate((day_width, 0)).label_above("Wednesday", 10, adj)
    thu = wed.copy().translate((day_width, 0)).label_above("Thursday", 10, adj)
    fri = thu.copy().translate((day_width, 0)).label_above("Friday", 10, adj)

    # add the days to the scene
    scene.add(bg)
    scene.add(mon)
    scene.add(tue)
    scene.add(wed)
    scene.add(thu)
    scene.add(fri)

    # fill in time labels (and draw horiz lines)
    for t in start_times:
        ypos = y_time(t, scene)
        h = HLine(Point(bg.min_x, ypos), bg.width)
        h.label_below_left(time_to_str(t), 8, 5, -8)
        scene.add(h)

    return scene

def add_sections(section_data, scene):
    """iterate over the list of Section objects, add each to the scene"""
    if not section_data:
        return scene

    for sect in section_data:
        r = timeslot(sect, scene)
        lines = [str(sect.num), sect.ta, 
                 time_to_str(sect.start) + " -- " + time_to_str(sect.end)]
        r.label_inside_multi(lines, 10, 5, -2).fill(1.0)
        scene.add(r)

    return scene

def schedule(lab_label="Testing", section_data=list(), outfile=sys.stdout):
    # schedules are on half-sheets
    paper_size = Point(inches(8.5), inches(4))
    s = Scene(Rectangle(Point(0, 0), paper_size))

    # draw the scheduling grid
    s = schedule_grid(lab_label, s)

    # add sections to schedule
    s = add_sections(section_data, s)

    # render the result
    s.render(outfile)

def main():
    # read in all .txt files
    data = parse_all()

    # each dictionary key is one room label (write to a separate file)
    for course_key in data:
        course_num, room_num = course_key
        section_data = data[course_key]
        course_num, room_num = course_key

        # render the collected information to file
        with open("%d_%d.ps" % (course_num, room_num), "w") as outfile:
            schedule("Physics %d | %d" % (course_num, room_num), section_data,
                     outfile)


if __name__ == "__main__":
    main()
