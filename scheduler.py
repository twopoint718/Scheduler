#!/usr/bin/python

import sys
import datetime
from sched_parser import parse_all, parse_file

# GLOBALS
verbose = True
generate_summary = True      # create the 12-up overview
generate_individual = True   # create separate files for each schedule

sum_font_size = 18
ind_font_size = 13
hdr_font_size = 32

summary_file = "summary.ps" # name for

start_times = [(7,45),  (8,50),  (9,55), (11,0), (12,5), (13,20),
               (14,25), (15,30), (16,35), (19,5), (21,0), (22,0), (23,0)]
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
label_offset = 72
schedule_height = 4 # inches
schedule_width  = 8 # inches
#########

# DERIVED
day_abbr = dict()
for (k,v) in zip(["M", "T", "W", "R", "F"], days): # "M" --> "Monday"
    day_abbr[k] = v
height = 72 * schedule_height
width = 72 * schedule_width
day_width = 1.0 * (width - label_offset) / 5


def main():
    # reference these so that they can be modified in main()
    global schedule_height
    global schedule_width
    global height
    global width
    global generate_summary
    global generate_individual

    if (len(sys.argv) == 2 and sys.argv[1] == "summary"):
        # just generate the summary
        generate_individual = False
        generate_summary = True

    if (len(sys.argv) == 3):
        # we're being called to process only a single file
        infile, outfile = sys.argv[1:]

        data = dict()
        key, lab_data = parse_file(infile) # "103,4320", { "R,14:25" :
                                           #                 ["330", "Yip"...]
                                           #               ...
                                           #             }
        data[key] = lab_data

        # tweak the globals
        schedule_height = 4
        schedule_width = 8
        height = 72 * schedule_height
        width = 72 * schedule_width
        xoff = 32
        yoff = 25 # 450
        scale = 0.95

        # get data for this lab
        key = infile.replace("_", ",")[:-4]
        lab_data = data[key]
        lab_num, room_num = key.split(",")

        # redirect output to the output file, OUTFILE, and fill it in
        f = open(outfile, "w")
        tmp = sys.stdout
        sys.stdout = f

        page_header(schedule_height + 1)
        scheduler(key, lab_data, xoff, yoff, scale, scale,
                  ind_font_size)
        print("showpage")
        print(r"%%Trailer")
        print(r"%%EOF")
        f.close()
        sys.stdout = tmp

        sys.exit(0)

    # now we know that we won't be parsing just a single file
    data = parse_all() # {'103,4320':{'T,16:35':('309', 'Ghanekar', '18:30'),
                       #              'T,14:25':('308', 'Puranik', '16:20'),...
                       #             },...
                       #  '104,3328':...
                       # }


    if generate_summary:
        # tweak the globals
        scale = 0.28
        schedule_height = schedule_width = 8
        height = 72 * schedule_height
        width = 72 * schedule_width

        if verbose:
            sys.stderr.write("Generating summary in [%s]..." % summary_file)
        # bind stout to a file and output to that
        f = open(summary_file, "w")
        tmp = sys.stdout
        sys.stdout = f

        # starting position
        xinit = 45
        xoff = xinit
        yoff = 565

        # spacing for each
        gap = 0.035
        ystep = (scale + gap) * height
        xstep = (scale + gap) * width

        page_header(11.5) # page height
        it = iter(sorted(data.items()))
        for lab_num, lab_data in it:
            scheduler(lab_num, lab_data, xoff, yoff, scale, scale,
                      sum_font_size)
            xoff = xoff + xstep
            if xoff > (width - xstep + xinit):
                xoff = xinit
                yoff = yoff - ystep

        # generate semester and year header
        margin = 10
        d = datetime.date.today()
        if d.month < 6:
            sem = "Spring"
        elif d.month < 9 and d.month > 5:
            sem = "Summer"
        else:
            sem = "Fall"
        y = d.year

        print("%% HEADING")
        print("/Helvetica findfont %d scalefont setfont" % hdr_font_size)
        center(8.5*72/2, 11.0*72 - hdr_font_size - margin, "%s %d" % (sem, y))

        # Finish it off
        print("showpage")
        print(r"%%Trailer")
        print(r"%%EOF")
        f.close()
        sys.stdout = tmp # reset to standard binding
        if verbose:
            sys.stderr.write("DONE\n")

    if generate_individual:
        # tweak the globals
        schedule_height = 4
        schedule_width = 8
        height = 72 * schedule_height
        width = 72 * schedule_width
        xoff = 32
        yoff = 25 # 450
        scale = 0.95

        it = iter(sorted(data.items()))
        for lab_num, lab_data in it:
            # create a file to hold this schedule
            fname = "_".join(lab_num.split(",")) + ".ps"
            if verbose:
                sys.stderr.write("Generating individual in [%s]..." % fname)
            f = open(fname, 'w')
            tmp = sys.stdout
            sys.stdout = f

            page_header(schedule_height + 1) # the page will be 5 inches tall
            scheduler(lab_num, lab_data, xoff, yoff, scale, scale,
                      ind_font_size)
            print("showpage")
            print(r"%%Trailer")
            print(r"%%EOF")
            f.close()
            sys.stdout = tmp
            if verbose:
                sys.stderr.write("DONE\n")

# create the box for an individual lab entry e.g. 103
def scheduler(lab_key, lab, xtr=20, ytr=20, xsc=0.95, ysc=0.95, fs=12):
    inches = lambda x: x * 72   # inch == 72pts
    label_offset = 72           # leave 1 in for col of times
    page_height = inches(schedule_height + 1)

    print("gsave")
    # scaling and translation
    print(xtr, ytr, "translate")
    print(xsc, ysc, "scale")
    print("/Helvetica findfont")
    print("%d scalefont setfont" % fs)

    #draw_grid(inches(8),inches(8))
    draw_grid(inches(schedule_width), inches(schedule_height))

    section, room = lab_key.split(",")

    # label the page (Course, room, day of week)
    print("gsave /Helvetica findfont %d scalefont setfont" % (fs * 2))
    center(width / 2.0, height + 30, "Physics %s | %s" % (section, room))
    print("grestore")
    for i in range(len(days)):
        dow_label_xpos = i * day_width + label_offset
        label(dow_label_xpos + 20 , height + 6, days[i])

    for k, v in list(lab.items()):
        d, t = k.split(",")
        if v[0] == "C":
            # consultation sections have no TA
            s, e = v
            ta = None
        else:
            s, ta, e = v

        # process
        day   = day_abbr[d]
        start = str2hm(t)
        end   = str2hm(e)
        sec   = str(s)
        if sec == "c" or sec == "C":
            schedule_block(day, start, end, ta, sec, fs, True)
        else:
            schedule_block(day, start, end, ta, sec, fs)
    print("grestore")

# Schedule utils
def schedule_block(day, start, end, ta, sec, fs=12, consultation=False):
    if consultation:
        lab_num_font = fs - 2
    else:
        lab_num_font = fs
    lab_font = fs - 4
    print("% BLOCK " + "%" * 71)
    xoffset = 5
    yoffset = 5
    xpos = days.index(day) * day_width + label_offset
    ypos = hm2pos(end)
    w = day_width
    h = min2len(dur(start,end))

    box(xpos, ypos, w, h, fill=True, color=1.0) # fill
    box(xpos, ypos, w, h)                       # outline

    # how far to make the next line in the text block start
    newline = lab_num_font - 2
    linepos = h - newline

    # label
    if consultation:
        # consultation sections have no section number and no TA, just start/end
        print("/Helvetica findfont %d scalefont setfont" % lab_num_font)
        label(xpos, ypos + linepos, "Consultation")
        linepos = linepos - newline
        print("/Helvetica findfont %d scalefont setfont" % lab_font)
        label(xpos, ypos + linepos, "%s -- %s" % (hm2str(start), hm2str(end)))
    else:
        print("/Helvetica findfont %d scalefont setfont" % lab_num_font)
        label(xpos, ypos + linepos, str(sec))
        linepos = linepos - newline
        print("/Helvetica findfont %d scalefont setfont" % lab_font)
        label(xpos, ypos + linepos, ta)
        linepos = linepos - newline
        label(xpos, ypos + linepos, "%s -- %s" % (hm2str(start), hm2str(end)))


def min2len(x):
    return x*(1.0*height/ dur(start_times[0], start_times[-1]))


def hm2pos(t):
    return height - min2len((hm2m(t) - hm2m(start_times[0])))


# Time utils
def hm2m(xxx_todo_changeme):
    """
    >>> hm2m((7, 45))
    465
    """
    (h, m) = xxx_todo_changeme
    return h * 60 + m

def m2hm(m):
    """
    >>> m2hm(1380)
    (23, 0)
    """
    return (m / 60, m % 60)

def dur(t1, t2):
    """
    >>> dur((7,45), (23,00))
    915
    """
    return hm2m(t2) - hm2m(t1)

def hm2str(t):
    h, m = t
    if h > 12:
        h = h - 12
    return "%d:%02d" % (h, m)

def str2hm(s):
    h, m = (s.strip()).split(":")
    return (int(h), int(m))

# PostScript utils
def hline(x,y, width):
    print("%HORIZ horizontal line at", (x,y), "and", width, "wide")
    print(x, y, "moveto")
    print(width, 0, "rlineto stroke")

def vline(x,y, height):
    print("%VERT vertical line at", (x,y), "and", height, "tall")
    print(x, y, "moveto")
    print(0, height, "rlineto stroke")

def box(x, y, w, h, fill=False, color=1.0):
    "Lower left and width x height"
    if h < 0 or w < 0:
        raise("box must have positive size")
    print("%BOX at", (x, y), "and", w, "by", h)
    print(x, y,        "moveto")
    print(w, 0,        "rlineto")
    print(0, h,        "rlineto")
    print(-1.0 * w, 0, "rlineto")
    print(0, -1.0 * h, "rlineto")
    if fill:
        print("gsave closepath")
        print(color, "setgray")
        print("fill")
        print("0 setgray grestore")
    else:
        print("closepath stroke")

def label(x,y,s, xoff=2, yoff=0):
    print("% LABEL")
    print(x + xoff, y + yoff, "moveto")
    print("(%s) show" % s)

def center(x, y, s):
    print(x, y, "moveto")
    print("(%s) dup stringwidth pop 2 div neg 0 rmoveto show" % s)

def draw_grid(width, height):
    min2len = lambda x: x*(1.0*height/ dur(start_times[0], start_times[-1]))
    hm2pos = lambda t: height - min2len((hm2m(t) - hm2m(start_times[0])))

    # draw outline
    box(0, 0, width, height, fill=True, color=0.80) # draw the fill
    box(0, 0, width, height)                        # draw the outline

    # draw timeslots
    for t in start_times:
        ypos = hm2pos(t)
        hline(0, ypos, width)

    # draw time labels inside of the time block they name
    time_yoff = schedule_height * 3
    for t in start_times:
        h, m = t
        ypos = hm2pos(t)
        if h < 23: # hack to label time "blocks" and not times
            label(5, ypos - time_yoff, hm2str(t))

    # leave some room for time labels on left
    for x in range(5):
        xpos = x*day_width + label_offset
        vline(xpos, 0, height)

def page_header(h=4):

    page_height = h * 72

    # begin DSC comment header
    print("""%%!PS-Adobe-2.0
%%%%BoundingBox: 0 0 612 %d
%%%%Creator: scheduler <cwilson@physics.wisc.edu>
%%%%Title: lab schedule
%%%%Pages: 1
%%%%PageOrder: Ascend
%%%%DocumentData: Clean7Bit
%%%%EndComments
%%%%BeginProlog
%%%%EndProlog
%%%%BeginSetup
<< /PageSize [612 %d] >> setpagedevice
%%%%EndSetup
%%%%Page: 1 1""" % (page_height, page_height))
    return


if __name__ == "__main__":
    main()


