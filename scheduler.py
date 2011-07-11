#!/bin/env python3
import sys
import time
from draw import HLine, Point, Rectangle, Scene, Text
from sched_parser import parse_all, parse_file
from sched_util import inches, start_times, timeslot, x_time, y_time, \
                       time_to_str, Section, timeslot_svg

def schedule_grid(title, scene, bounding_box, font_base=12):
    """Draws a standard Schedule grid:
    """
    margin = 5

    # add background (shaded area)
    title_font = font_base + 4
    o, e = bounding_box.origin, bounding_box.extent
    bg = Rectangle(o, e)
    bg = bg.shrink(margin).lower(30).fill(0.8).label_above(title, title_font, 6)

    day_width = bg.width / 6.0

    # label column on left
    lab = Rectangle(bg.origin.copy(), Point(bg.min_x + day_width, bg.max_y))

    # add days
    adj = -2 # move labels slightly down
    fs = font_base - 2
    mon = lab.copy().translate((day_width, 0)).label_above("Monday", fs, adj)
    tue = mon.copy().translate((day_width, 0)).label_above("Tuesday", fs, adj)
    wed = tue.copy().translate((day_width, 0)).label_above("Wednesday", fs, adj)
    thu = wed.copy().translate((day_width, 0)).label_above("Thursday", fs, adj)
    fri = thu.copy().translate((day_width, 0)).label_above("Friday", fs, adj)

    # add the days to the scene
    scene.add(bg, True) # make this the working canvas
    scene.add(mon)
    scene.add(tue)
    scene.add(wed)
    scene.add(thu)
    scene.add(fri)

    # fill in time labels (and draw horiz lines)
    linespacing = int(-1.0 * fs / 1.5)
    for t in start_times[:-1]:
        ypos = y_time(t, scene)
        h = HLine(Point(bg.min_x, ypos), bg.width)
        h.label_below_left(time_to_str(t), fs, 5, linespacing)
        scene.add(h)

    return scene

def add_sections(section_data, scene, bounding_box, font_base=12):
    """iterate over the list of Section objects, add each to the scene"""
    if not section_data:
        return scene

    v_tweak = -1.0 * font_base / 6
    h_tweak = font_base / 2
    for sect in section_data:
        r = timeslot(sect, scene)
        lines = [str(sect.num), sect.ta, 
                 time_to_str(sect.start) + " -- " + time_to_str(sect.end)]
        r.label_inside_multi(lines, font_base-2, h_tweak, v_tweak).fill(1.0)
        scene.add(r)

    return scene

def add_sections_svg(section_data, scene, bounding_box, font_base=12):
    if not section_data:
        return scene

    v_tweak = font_base / 5
    h_tweak = font_base / 2
    for sect in section_data:
        r = timeslot_svg(sect, scene)
        lines = [str(sect.num), sect.ta, 
                 time_to_str(sect.start) + " -- " + time_to_str(sect.end)]
        r.label_inside_multi_svg(lines, font_base-2, h_tweak, v_tweak).fill(1.0)
        scene.add(r)

    return scene

def add_section_svg(sect, scene, bounding_box, font_base=12):
    if not sect:
        return scene

    v_tweak = font_base / 5
    h_tweak = font_base / 2
    r = timeslot_svg(sect, scene)
    lines = [str(sect.num), sect.ta, 
             time_to_str(sect.start) + " -- " + time_to_str(sect.end)]
    r.label_inside_multi_svg(lines, font_base-2, h_tweak, v_tweak).fill(1.0)
    scene.add(r)

    return scene

def schedule(lab_label="Testing", 
             section_data=list(), 
             outfile=sys.stdout,
             bounding_box=Rectangle(Point(0,0), Point(inches(8.5), inches(4)))):
    # schedules are on half-sheets
    s = Scene(bounding_box)

    # draw the scheduling grid
    s = schedule_grid(lab_label, s, bounding_box)

    # add sections to schedule
    s = add_sections(section_data, s, bounding_box)

    # render the result
    if format == "SVG":
        s.render_svg(outfile)
    else:
        s.render(outfile)

def summary(lab_data,
            bounding_box=Rectangle(Point(0,0), Point(inches(8.5), inches(11))),
            format="PS"):

    bounding_box = bounding_box.translate((8, -36))
    s = Scene(bounding_box)

    # draw reduced-size schedules (2.5 x 2.5)
    placements = list()
    gap = inches(0.25)
    w = inches(2.5)
    x_off = gap + w
    y_off = x_off
    for j in range(3):
        for i in range(3):
            p1 = Point(bounding_box.min_x + i * x_off,
                       bounding_box.max_y - (j+1) * y_off)
            p2 = Point(bounding_box.min_x + (i+1) * x_off,
                       bounding_box.max_y - j * y_off)
            placements.append(Rectangle(p1, p2))
            
    # place each available course into its own mini layout
    for (course_key, bb) in zip(lab_data, placements):
        course_num, room_num = course_key
        section_data = lab_data[course_key]

        s = schedule_grid("Physics %d | %d" % (course_num, room_num), s, bb, 8)
        s = add_sections(section_data, s, bb, 8)

    # label the summary
    t = time.localtime(time.time())
    mon = t.tm_mon
    yr = t.tm_year
    if mon in [12, 1, 2, 3, 4]:
        session = "Spring"
    elif mon in [8, 9, 10, 11]:
        session = "Fall"
    else:
        session = "Summer"
    label = "%s %d" % (session, yr)
    s.add(Text(Point(inches(8.5)/2.0, inches(11) - inches(0.50)), 
               label, True, "Helvetica", 36))
    
    with open("summary.ps", "w") as outfile:
        s.render(outfile)

def schedule_grid_svg(title, scene, bounding_box, font_base=12):
    """Draws standard schedule grid, SVG
    """
    margin = 5
    
    # add background (shaded area)
    title_font = font_base + 4
    o, e = bounding_box.origin, bounding_box.extent
    bg = Rectangle(o, e)
    bg = bg.shrink(margin).lower_svg(40).fill(0.8).label_above_svg(title, title_font, 12)

    day_width = bg.width / 6.0

    # label column on left
    lab = Rectangle(bg.origin.copy(), Point(bg.min_x + day_width, bg.max_y))

    # add days
    adj = -2 # move labels slightly down
    fs = font_base - 2
    mon = lab.copy().fill(0.8).translate((day_width, 0)).label_above_svg("Monday", fs, adj)
    tue = mon.copy().fill(0.8).translate((day_width, 0)).label_above_svg("Tuesday", fs, adj)
    wed = tue.copy().fill(0.8).translate((day_width, 0)).label_above_svg("Wednesday", fs, adj)
    thu = wed.copy().fill(0.8).translate((day_width, 0)).label_above_svg("Thursday", fs, adj)
    fri = thu.copy().fill(0.8).translate((day_width, 0)).label_above_svg("Friday", fs, adj)

    # add the days to the scene
    scene.add(bg, True) # make this the working canvas
    scene.add(mon)
    scene.add(tue)
    scene.add(wed)
    scene.add(thu)
    scene.add(fri)

    # fill in time labels (and draw horiz lines)
    linespacing = int(-1.0 * fs / 0.8)
    for t in reversed(start_times[:-1]):
        ypos = bg.max_y - y_time(t, scene) + bg.min_y
        h = HLine(Point(bg.min_x, ypos), bg.width)
        h.label_below_left_svg(time_to_str(t), fs, 5, -linespacing)
        scene.add(h)

    return scene

def schedule_svg(lab_label="Testing",
                 section_data=list(),
                 outfile=sys.stdout,
                 bounding_box=Rectangle(Point(0,0), Point(850, 400))):

    # schedules are on half-sheets
    s = Scene(bounding_box)

    # draw the scheduling grid
    s = schedule_grid_svg(lab_label, s, bounding_box)

    # add sections to schedule
    s = add_sections_svg(section_data, s, bounding_box)

    # render the result
    s.render_svg(outfile)

def summary_svg(data):
    pass
    
def main(format="PS"):
    # read in all .txt files
    data = parse_all()

    # each dictionary key is one room label (write to a separate file)
    for course_key in data:
        course_num, room_num = course_key
        section_data = data[course_key]
        course_num, room_num = course_key

        # render the collected information to file
        if format == "SVG":
            with open("%d_%d.svg" % (course_num, room_num), "w") as outfile:
                schedule_svg("Physics %d | %d" % (course_num, room_num), 
                             section_data, outfile)
        else: # PS default
            with open("%d_%d.ps" % (course_num, room_num), "w") as outfile:
                schedule("Physics %d | %d" % (course_num, room_num), 
                         section_data, outfile)
    # generate summary
    if format == "SVG":
        summary_svg(data)
    else:
        summary(data)

if __name__ == "__main__":
    main(format="SVG")
