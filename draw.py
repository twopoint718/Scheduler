import math

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

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
        return Point(self.x * s, self.y * s)

class Scene:
    def __init__(self, bounds):
        self.objects = list()
        self.bounds = bounds

    def add(self, obj):
        if type(obj).__name__ == "HLine": # set HLine to width of scene
            obj.bounds = Rectangle(Point(0, obj.h), Point(self.bounds.max_x, obj.h))
        if type(obj).__name__ == "VLine":
            obj.bounds = Rectangle(Point(obj.w, 0), Point(obj.w, self.bounds.max_y))
        if not obj.contained_in(self.bounds):
            raise ValueError("Object " + obj + " is outside the scene")
        self.objects.append(obj)
    
    def render(self):
        for obj in self.objects:
            obj.render()

class Rectangle:
    def __init__(self, origin, extent):
        self.origin = origin
        self.extent = extent
        if origin > extent:
            raise ValueError("Origin is greater than far corner!")
        self.bounds = Rectangle(origin, extent)
        self.min_x = origin.x
        self.max_x = extent.x
        self.min_y = origin.y
        self.max_y = extent.y

    def contained_in(self, rect):
        if self.origin.x < rect.origin.x or self.extent.x > rect.extent.x:
            return False
        if self.origin.y < rect.origin.y or self.extent.y > rect.extent.y:
            rerturn False
        return True 

    def render(self):
        box(self.origin, self.extent)

class HLine:
    def __init__(self, h, width=None):
        self.h = h

#
# Drawing primitives
#

    
