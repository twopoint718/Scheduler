import math
import sys

class Point:
    """Point is a basic 2-d Cartesian pair.  This is used as the corners of
    of a Rectangle.  Some operators are defined on points:
    ('+', '-', '==', '<', '>')
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def copy(self):
        """return a new object that's the same as this one"""
        return Point(self.x, self.y)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __lt__(self, other):
        return (self.x**2 + self.y**2) < (other.x**2 + other.y**2)

    def __gt__(self, other):
        return (self.x**2 + self.y**2) > (other.x**2 + other.y**2)

    def scale(self, s):
        """scaling by a scalar value"""
        self.x = self.x * s
        self.y = self.y * s
        return self

    def slide(self, i):
        """move point along a line parallel (or possibly equal) to the line
        y = x
        """
        self.x = self.x + i
        self.y = self.y + i
        return self

    def translate(self, mov):
        """slide the point by an amount given in the tuple mov, (a, b)
        would slide by x+a, y+b
        """
        a, b = mov
        self.x = self.x + a
        self.y = self.y + b
        return self
    
    def __repr__(self):
        return "(%d, %d)" % (self.x, self.y)

class Scene:
    """Scene is a list of geometric objects and a Rectangle boundary.  The
    objects are constrained to fit within the bounds of the scene"""
    def __init__(self, bounds):
        self.objects = list()
        self.bounds = bounds

    def add(self, obj):
        """add an object to the scene if it lies fully within the bounds"""
        if not obj.contained_in(self.bounds):
            raise ValueError("Object [%s] is outside the scene" % obj)
        self.objects.append(obj)
    
    def render(self, toFile=sys.stdout):
        """create postscript output for all the objects in the scene by
        calling each of their respective render methods
        """
        render_preamble(self.bounds, toFile)
        for obj in self.objects:
            obj.render(toFile)
        render_footer(toFile)

class Rectangle:
    """Defined by the lower-left corner (origin) and the upper-right corner
    (extent).  It is a ValueError for the lower-left corner to be farther
    from the point (0, 0) than the upper-right corner.

    Most (all?) Rectangle-modifying operations make changes to the internal
    representation, but also return the Rectangle object so that you can do
    some mean method chaining:
    
    bg = Rectangle(...)
    bg = bg.shrink(5).lower(30).fill(0.8).label_above("Schedule", 18, 8)

    The result is the combination of applying all those transformations.  I
    don't know how pythonic this is but I think it's cool.
    """
    def __init__(self, origin, extent):
        self.__resize(origin, extent)
        self.fill_color = 1.0
        self.filled = False
        self.label = None

    def __resize(self, origin, extent):
        """(re)calculates various internal measurements, this is called
        after any operation that moves a corner
        """
        self.origin = origin
        self.extent = extent
        if self.origin > self.extent:
            raise ValueError("Origin is greater than far corner!")
        self.min_x = self.origin.x
        self.max_x = self.extent.x
        self.min_y = self.origin.y
        self.max_y = self.extent.y
        self.width = self.max_x - self.min_x
        self.height = self.max_y - self.min_y
        self.center_x = self.min_x + self.width / 2.0
        self.center_y = self.min_y + self.height / 2.0

    def contained_in(self, rect):
        """determine if this rectangle lies completely inside (or on top)
        of another one
        """
        if self.origin.x < rect.origin.x or self.extent.x > rect.extent.x:
            return False
        if self.origin.y < rect.origin.y or self.extent.y > rect.extent.y:
            return False
        return True

    def copy(self):
        """return a Rectangle with the same origin and extent"""
        return Rectangle(self.origin.copy(), self.extent.copy())

    def corners(self):
        """get copies of the origin and extent of this rectangle"""
        return (self.origin.copy(), self.extent.copy())

    def fill(self, color=0.0):
        """fill the rectangle with color where color is the fraction of
        gray (1.0 == white)
        """
        self.filled = True
        self.fill_color = color
        return self

    def label_above(self, txt, fontsize=12, vbump=0):
        """create a centered label above the rectangle"""
        p = Point(self.center_x, self.max_y + fontsize/2 + vbump)
        self.label = Text(p, txt, size=fontsize, font="Helvetica", hCenter=True)
        return self

    def label_above_left(self, txt, fontsize=12.0, hbump=0):
        """create a label above and to the left of the rectangle"""
        p = Point(self.origin.x + hbump, self.max_y + fontsize/2)
        self.label = Text(p, txt, size=fontsize, font="Helvetica", hCenter=False)
        return self

    def label_below_left(self, txt, fontsize=12.0, hbump=0, vbump=0):
        p = Point(self.origin.x + hbump, self.min_y - fontsize/2 + vbump)
        self.label = Text(p, txt, size=fontsize, font="Helvetica", hCenter=False)
        return self

    def label_inside(self, txt, fontsize=10):
        """center the label both horizontally and vertically inside the
        rectangle. txt can be a list of strings, these will be formatted
        one to a line with a bigger header line
        """
        p = Point(self.center_x, self.center_y - fontsize/2.7)
        self.label = Text(p, txt, size=fontsize, font="Helvetica", hCenter=True)
        return self

    def label_inside_multi(self, txt, fontsize=10, hbump=0, vbump=0):
        """label inside the rectangle starting in the upper left, suitable
        for labeling section information
        """
        p = Point(self.min_x + hbump, self.max_y + vbump)
        self.label = Text(p, txt, size=fontsize, font="Helvetica", hCenter=False)
        return self

    def render(self, toFile=sys.stdout):
        """call to the low-level drawing primitives"""
        b = box(self.origin, self.extent, self.filled, self.fill_color,
                toFile)
        self.label.render(toFile)
        return b

    def shrink(self, x):
        "return a rectangle that's smaller by x at each margin"
        o, e = self.origin.slide(x), self.extent.slide(-1 * x)
        self.__resize(o, e)
        return self

    def shift_right(self, i):
        """resize the rect by moving the origin to the right by i"""
        o, e = Point(self.origin.x + i, self.origin.y), self.extent
        self.__resize(o, e)
        return self

    def translate(self, mov):
        """Move the rectangle without resize by MOV (an x-y tuple)"""
        o, e = self.origin.translate(mov), self.extent.translate(mov)
        self.__resize(o, e)
        return self

    def lower(self, i):
        """decrease the height by x (from the top)"""
        e = Point(self.extent.x, self.extent.y - i)
        o = self.origin
        self.__resize(o, e)
        return self

    def __repr__(self):
        return "Rectangle(%s, %s)" % (self.origin, self.extent)

class HLine(Rectangle):
    """HLine is just a rectangle constrained to have zero vertical height
    """
    def __init__(self, origin, width):
        self.width = width
        self.origin = origin
        self.extent = Point(origin.x + width, origin.y)
        Rectangle.__init__(self, self.origin, self.extent)

    def __repr__(self):
        return "Horizontal(%s, width:%d)" % (self.origin, self.width)

class VLine(Rectangle):
    """VLine is just a rectangle constrained to have zero horizontal width
    """
    def __init__(self, origin, height):
        self.height = height
        self.origin = origin
        self.extent = Point(origin.x, origin.y + height)
        Rectangle.__init__(self, self.origin, self.extent)

    def __repr__(self):
        return "Vertical(%s, height:%d)" % (self.origin, self.height)

class Text:
    """A Text object.  Often this is part of a Rectangle instance as its
    label.  This can be multiline if txt is a list of strings
    """
    def __init__(self, pos, txt, hCenter=True, font="Helvetica", size=12):
        self.pos = pos
        self.txt = txt
        self.hCenter = hCenter
        self.font = font
        self.size = size

    def render(self, toFile=sys.stdout):
        """call to the low-level drawing primitives"""
        # render multiline text
        if type(self.txt) == type(list()):
            offset = self.size
            text(Point(self.pos.x, self.pos.y - offset), self.txt[0],
                 self.font, self.size, self.hCenter, toFile)
            for line in self.txt[1:]:
                offset = offset + (self.size - 2)
                text(Point(self.pos.x, self.pos.y - offset), line, self.font,
                     self.size - 2, self.hCenter, toFile)

            return "\n".join(self.txt)

        # single line of text
        return text(self.pos, self.txt, self.font, self.size, self.hCenter, toFile)
    
    def __repr__(self):
        return "Text(%s)" % self.txt

#
# Drawing primitives (here be PostScript-specific dragons)
#
def render_preamble(rect, toFile=sys.stdout):
    """Emit the required boilerplate for a postscript document"""
    page_height = rect.max_y - rect.min_y
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
%%%%Page: 1 1""" % (page_height, page_height), file=toFile)
    return

def render_footer(toFile=sys.stdout):
    """Emit the required trailing boilerplate for a postscript document"""
    print("showpage", file=toFile)
    print("%%Trailer", file=toFile)
    print("%%EOF", file=toFile)

def box(p1, p2, fill=False, color=1.0, toFile=sys.stdout):
    """Draw a basic rectangle with corners at p1 and p2.  Pretty much a
    low-level mapping of the Rectangle object"""
    w = p2.x - p1.x
    h = p2.y - p1.y
    lines = list()
    lines.append("%% BOX at %s %f by %f" % (p1, w, h))
    lines.append("%f %f moveto" % (p1.x, p1.y))
    lines.append("%f 0 rlineto" % w)
    lines.append("0 %f rlineto" % h)
    lines.append("%f 0 rlineto" % (-1.0*w))
    lines.append("0 %f rlineto" % (-1.0*h))
    if fill:
        lines.append("gsave closepath")
        lines.append("%0.2f setgray" % color)
        lines.append("fill")
        lines.append("0 setgray grestore")
    lines.append("closepath stroke")
    print("\n".join(lines), file=toFile)
    return lines

def text(pt, txt, font="Helvetica", size=12, center=True, toFile=sys.stdout):
    """Draw a line of PostScript text. Normally, code to center the line
    horizontally is emitted."""
    lines = list()
    lines.append("%% LABEL at %s (%s)" % (pt, txt))
    lines.append("%f %f moveto" % (pt.x, pt.y))
    lines.append("/%s findfont %f scalefont setfont" % (font, size))
    if center:
        lines.append("(%s) dup stringwidth pop 2 div neg 0 rmoveto show" % txt)
    else:
        lines.append("(%s) show" % txt)
    print("\n".join(lines), file=toFile)
    return lines
