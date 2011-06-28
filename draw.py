import math

class Point:
    """Point is a basic 2-d Cartesian pair"""
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def copy(self):
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
        self.x = self.x * s
        self.y = self.y * s
        return self

    def slide(self, i):
        """Move point along the line y = x"""
        return Point(self.x + i, self.y + i)

    def translate(self, mov):
        a, b = mov
        self.x = self.x + a
        self.y = self.y + b
        return self
    
    def __repr__(self):
        return "(%d, %d)" % (self.x, self.y)

class Scene:
    """Scene is a list of geometric objects.  The objects are constrained
    to fit within the bounds of the scene"""
    def __init__(self, bounds):
        self.objects = list()
        self.bounds = bounds

    def add(self, obj):
        if not obj.contained_in(self.bounds):
            raise ValueError("Object [%s] is outside the scene" % obj)
        self.objects.append(obj)
    
    def render(self):
        render_preamble(self.bounds)
        for obj in self.objects:
            obj.render()
        render_footer()

class Rectangle:
    """Defined by the lower-left corner and the upper-right corner
    Constructor: ORIGIN :: Point, EXTENT :: Point"""
    def __init__(self, origin, extent):
        self.resize(origin, extent)
        self.fill_color = 1.0
        self.filled = False
        self.label = None

    def resize(self, origin, extent):
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
        if self.origin.x < rect.origin.x or self.extent.x > rect.extent.x:
            return False
        if self.origin.y < rect.origin.y or self.extent.y > rect.extent.y:
            return False
        return True

    def copy_geom(self):
        """Return a Rectangle with the same origin and extent"""
        return Rectangle(self.origin.copy(), self.extent.copy())

    def fill(self, color=0.0):
        """Fill the rectangle with COLOR (fraction gray)"""
        self.filled = True
        self.fill_color = color
        return self

    def label_above(self, txt, fontsize=12):
        p = Point(self.center_x, self.max_y + fontsize/2)
        self.label = Text(p, txt, size=fontsize, font="Helvetica", hCenter=True)
        return self

    def label_inside(self, txt, fontsize=12):
        p = Point(self.center_x, self.center_y)
        self.label = Text(p, txt, size=fontsize, font="Helvetica", hCenter=True)

    def render(self):
        if self.label:
            self.label.render()
        if self.fill:
            return box(self.origin, self.extent, self.filled, self.fill_color)
        return box(self.origin, self.extent)

    def shrink(self, x):
        "return a rectangle that's smaller by x at each margin"
        o, e = self.origin.slide(x), self.extent.slide(-1 * x)
        self.resize(o, e)
        return self

    def shift_right(self, i):
        """resize the rect by moving the origin to the right by i"""
        o, e = Point(self.origin.x + i, self.origin.y), self.extent
        self.resize(o, e)
        return self

    def translate(self, mov):
        """Move the rectangle without resize by MOV (an x-y tuple)"""
        o, e = self.origin.translate(mov), self.extent.translate(mov)
        self.resize(o, e)
        return self

    def lower(self, i):
        """decrease the height by x (from the top)"""
        e = Point(self.extent.x, self.extent.y - i)
        o = self.origin
        self.resize(o, e)
        return self

    def __repr__(self):
        return "Rectangle(%s, %s)" % (self.origin, self.extent)

class HLine(Rectangle):
    """HLine is just a rectangle constrained to have zero vertical
    height, it has an ORIGIN (Point) and a WIDTH (int)
    Constructor: ORIGIN :: Point, WIDTH :: int"""
    def __init__(self, origin, width):
        self.width = width
        self.origin = origin
        self.extent = Point(origin.x + width, origin.y)
        Rectangle.__init__(self, self.origin, self.extent)

    def __repr__(self):
        return "Horizontal(%s, width:%d)" % (self.origin, self.width)

class VLine(Rectangle):
    """VLine is just a rectangle constrained to have zero horizontal width,
    it has an ORIGIN (Point) and a HEIGHT (int)
    Constructor: ORIGIN :: Point, HEIGHT :: int"""
    def __init__(self, origin, height):
        self.height = height
        self.origin = origin
        self.extent = Point(origin.x, origin.y + height)
        Rectangle.__init__(self, self.origin, self.extent)

    def __repr__(self):
        return "Vertical(%s, height:%d)" % (self.origin, self.height)

class Text:
    def __init__(self, pos, txt, hCenter=True, font="Helvetica", size=12):
        self.pos = pos
        self.txt = txt
        self.hCenter = hCenter
        self.font = font
        self.size = size

    def render(self):
        if self.hCenter and self.font == "Helvetica" and self.size == 12:
            return text(self.pos, self.txt)
        return text(self.pos, self.txt, self.font, self.size, self.hCenter)
    
    def __repr__(self):
        return "Text(%s)" % self.txt

#
# Drawing primitives
#
def render_preamble(rect):
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
%%%%Page: 1 1""" % (page_height, page_height))
    return

def render_footer():
    print("showpage")
    print("%%Trailer")
    print("%%EOF")

def box(p1, p2, fill=False, color=1.0):
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
    else:
        lines.append("closepath stroke")
    print("\n".join(lines))
    return lines

def text(pt, txt, font="Helvetica", size=12, center=True):
    lines = list()
    lines.append("%% LABEL at %s (%s)" % (pt, txt))
    lines.append("%f %f moveto" % (pt.x, pt.y))
    lines.append("/%s findfont %f scalefont setfont" % (font, size))
    if center:
        lines.append("(%s) dup stringwidth pop 2 div neg 0 rmoveto show" % txt)
    else:
        lines.append("(%s) show" % txt)
    print("\n".join(lines))
    return lines
