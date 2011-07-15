#!/bin/env python3
from draw import Point, Scene, Rectangle, HLine, Text
from sched_parser import parse_line, parse_all_lines, parse_file, parse_all
from sched_util import *
import unittest
import os
import tempfile

class TestPoint(unittest.TestCase):
    def setUp(self):
        self.null = open(os.devnull, "w")
        self.p1 = Point(0,0)
        self.p2 = Point(1,2)
        self.p3 = Point(2,1)

    def testAdd(self):
        self.assertEqual(Point(3,3), self.p2 + self.p3)
        self.assertIsNot(Point(1,2), self.p2)
        self.assertIsNot(self.p1, self.p1 + self.p2)
        self.assertIsNot(self.p2, self.p1 + self.p2)

    def testSub(self):
        self.assertEqual(Point(0,0), self.p2 - Point(1,2))
        self.assertIsNot(self.p1, self.p1 - self.p2)
        self.assertIsNot(self.p2, self.p1 - self.p2)

    def testLessThan(self):
        self.assertTrue(self.p1 < self.p2)
        self.assertFalse(self.p2 < self.p3)

    def testScale(self):
        self.assertEqual(Point(0,0), self.p1.scale(10))
        self.assertEqual(Point(2,4), self.p2.scale(2))


class TestScene(unittest.TestCase):
    def setUp(self):
        self.null = open(os.devnull, "w")
        self.r = Rectangle(Point(0,0), Point(10,10))
        self.s = Scene(self.r)

    def testAdd(self):
        r = Rectangle(Point(1,1), Point(2,2))
        r1 = Rectangle(Point(-1,1), Point(2,2))
        self.s.add(r)
        self.assertRaises(ValueError, self.s.add, r1)

    def testGetCanvas(self):
        self.assertIsNone(self.s.get_canvas())
        r = Rectangle(Point(2,2), Point(3,3))
        self.s.add(r)
        self.assertIsNotNone(self.s.get_canvas())
        self.assertEqual(self.s.get_canvas(), r)

    def testRender(self):
        r = Rectangle(Point(5,5), Point(8,8))
        self.s.add(r)
        self.assertEqual(self.s.render(self.null), None)


class TestRectangle(unittest.TestCase):
    def setUp(self):
        self.null = open(os.devnull, "w")
        self.r = Rectangle(Point(0,0), Point(10,10))

    def testContained_in(self):
        r1 = Rectangle(Point(1,1), Point(2,2))
        r2 = Rectangle(Point(0,0), Point(10,10))
        r3 = Rectangle(Point(1,1), Point(11,10))
        r4 = Rectangle(Point(1,1), Point(10,11))
        self.assertTrue(r1.contained_in(self.r))
        self.assertTrue(r2.contained_in(self.r))
        self.assertFalse(r3.contained_in(self.r))
        self.assertFalse(r4.contained_in(self.r))

    def testCopy(self):
        rc = self.r.copy()
        self.assertIsNot(rc, self.r)

        self.assertEqual(rc.origin, self.r.origin)
        self.assertEqual(rc.extent, self.r.extent)

        self.assertIsNot(rc.origin, self.r.origin)
        self.assertIsNot(rc.extent, self.r.extent)

    def testCorners(self):
        o, e = self.r.corners()
        self.assertIsNot(o, self.r.origin)
        self.assertIsNot(e, self.r.extent)

        self.assertEqual(o, self.r.origin)
        self.assertEqual(e, self.r.extent)

    def testLabelAbove(self):
        self.r.label_above("testing")
        self.assertIsInstance(self.r.label, Text)
        self.assertTrue(self.r.label.pos.y > self.r.extent.y) # above

    def testLabelAboveLeft(self):
        self.r.label_above_left("testing")
        self.assertIsInstance(self.r.label, Text)
        self.assertTrue(self.r.label.pos.y > self.r.extent.y) # above
        self.assertTrue(self.r.label.pos.x < self.r.center_x) # left

    def testLabelBelowLeft(self):
        self.r.label_below_left("testing")
        self.assertIsInstance(self.r.label, Text)
        self.assertTrue(self.r.label.pos.y < self.r.origin.y) # below
        self.assertTrue(self.r.label.pos.x < self.r.center_x) # left

    def testLabelInside(self):
        self.r.label_inside("testing")
        self.assertIsInstance(self.r.label, Text)
        self.assertEqual(self.r.label.pos.x, self.r.center_x) # horiz. center
        self.assertTrue(self.r.label.pos.y < self.r.center_y) # vert lower a bit

    def testLabelInsideMulti(self):
        self.r.label_inside_multi("testing")
        self.assertIsInstance(self.r.label, Text)
        self.assertEqual(self.r.label.pos.x, self.r.min_x)
        self.assertEqual(self.r.label.pos.y, self.r.max_y)

    def testShrink(self):
        self.r.shrink(1)
        self.assertEqual(self.r.origin, Point(1,1))
        self.assertEqual(self.r.extent, Point(9,9))

    def testShiftRight(self):
        self.r.shift_right(10)
        self.assertEqual(self.r.origin, Point(10,0))  # shifted
        self.assertEqual(self.r.extent, Point(10,10)) # NOT shifted

    def testTranslate(self):
        o = self.r.origin
        e = self.r.extent
        self.r.translate((2, 3))
        self.assertEqual(self.r.origin, Point(2,3))
        self.assertEqual(self.r.extent, Point(12, 13))

    def testLower(self):
        self.r.lower(5)
        self.assertEqual(self.r.origin, Point(0,0))
        self.assertEqual(self.r.extent, Point(10,5))

    def testFill(self):
        self.r.fill(0.5)
        self.assertEqual(self.r.render(self.null),
                         ['% BOX at (0, 0) 10.000000 by 10.000000',
                          '0.000000 0.000000 moveto',
                          '10.000000 0 rlineto',
                          '0 10.000000 rlineto',
                          '-10.000000 0 rlineto',
                          '0 -10.000000 rlineto',
                          'gsave closepath',
                          '0.50 setgray',
                          'fill',
                          '0 setgray grestore',
                          'closepath stroke'])


    def testRender(self):
        self.assertEqual(self.r.render(self.null), 
                         ['% BOX at (0, 0) 10.000000 by 10.000000', 
                          '0.000000 0.000000 moveto', 
                          '10.000000 0 rlineto', 
                          '0 10.000000 rlineto', 
                          '-10.000000 0 rlineto', 
                          '0 -10.000000 rlineto', 
                          'closepath stroke'])

    def testLabelRender(self):
        self.r.label_above("testing")
        self.assertIsNotNone(self.r.label)
        self.assertEqual(self.r.render(self.null),
                         ['% BOX at (0, 0) 10.000000 by 10.000000', 
                          '0.000000 0.000000 moveto',
                          '10.000000 0 rlineto',
                          '0 10.000000 rlineto',
                          '-10.000000 0 rlineto',
                          '0 -10.000000 rlineto',
                          'closepath stroke',
                          '% LABEL at (5, 16) (testing)',
                          '5.000000 16.000000 moveto',
                          '/Helvetica findfont 12.000000 scalefont setfont',
                          '(testing) dup stringwidth pop 2 div neg 0 rmoveto show'])

    def testRepr(self):
        self.assertEqual("%s" % self.r, "Rectangle((0, 0), (10, 10))")

    def testResizeException(self):
        self.assertRaises(ValueError, Rectangle, Point(1,1), Point(0,0))


class TestHLine(unittest.TestCase):
    def setUp(self):
        self.null = open(os.devnull, "w")
        self.h = HLine(Point(0,0), 5)

    def testRepr(self):
        self.assertEqual("%s" % self.h, "Horizontal((0, 0), width:5)")

    def testRender(self):
        self.assertEqual(self.h.render(self.null),
                         ['% BOX at (0, 0) 5.000000 by 0.000000', 
                          '0.000000 0.000000 moveto', 
                          '5.000000 0 rlineto',
                          '0 0.000000 rlineto',
                          '-5.000000 0 rlineto',
                          '0 -0.000000 rlineto',
                          'closepath stroke'])


class TestText(unittest.TestCase):
    def setUp(self):
        self.null = open(os.devnull, "w")
        self.t = Text(Point(0,0), "testing")
        self.tm = Text(Point(0,0), ["Multi", "Line", "Text"])
        self.toffc = Text(Point(0,0), "testing", False)

    def testContained_in(self):
        r1 = Rectangle(Point(100,100), Point(200,200))
        self.assertTrue(self.t.contained_in(r1)) # always true 

    def testRender(self):
        self.assertEqual(self.t.render(self.null), 
                         ['% LABEL at (0, 0) (testing)', 
                          '0.000000 0.000000 moveto', 
                          '/Helvetica findfont 12.000000 scalefont setfont', 
                          '(testing) dup stringwidth pop 2 div neg 0 rmoveto show'])

    def testRenderMultiline(self):
        self.assertEqual(self.tm.render(self.null),
                         ['% LABEL at (0, -12) (Multi)',
                          '0.000000 -12.000000 moveto',
                          '/Helvetica findfont 12.000000 scalefont setfont',
                          '(Multi) dup stringwidth pop 2 div neg 0 rmoveto show',
                          '% LABEL at (0, -22) (Line)',
                          '0.000000 -22.000000 moveto',
                          '/Helvetica findfont 10.000000 scalefont setfont',
                          '(Line) dup stringwidth pop 2 div neg 0 rmoveto show',
                          '% LABEL at (0, -32) (Text)',
                          '0.000000 -32.000000 moveto',
                          '/Helvetica findfont 10.000000 scalefont setfont',
                          '(Text) dup stringwidth pop 2 div neg 0 rmoveto show'])

    def testOffCenter(self):
        self.assertEqual(self.toffc.render(self.null),
                        ['% LABEL at (0, 0) (testing)',
                         '0.000000 0.000000 moveto',
                         '/Helvetica findfont 12.000000 scalefont setfont', 
                         '(testing) show'])

    def testRepr(self):
        self.assertEqual("%s" % self.t, "Text(testing)")


class TestParser(unittest.TestCase):
    def setUp(self):
        self.s1 = Section('M', (12,  5), "301",      "Ojalvo",  (14,  0))
        self.s2 = Section('T', (14, 25), "(321) 301", "Dhorkah", (17, 25))
        self.s3 = Section('F', ( 8,  0), "C",        "",        (15,  0))
        self.sampleLine1 = "M,12:05 301     Ojalvo    14:00"
        self.sampleLine2 = "T,14:25 (321)301        Dhorkah         17:25"
        self.sampleLine3 = "F,8:00  C                               15:00"
        self.sampleText1 = """
M,12:05 301     Ojalvo    14:00
M,14:25 302     Carmody   16:20
M,16:35 303     Ojalvo    18:30
M,19:05 304     N/A       21:00
# comment line
xxx
T,7:45  305     Carmody    9:40
T,9:55  306     Zeng      11:50
T,12:05 307     Zeng      14:00
"""
        self.sampleParse1 = [Section('M', (12, 5), '301', 'Ojalvo', (14, 0)),
                             Section('M', (14, 25), '302', 'Carmody', (16, 20)),
                             Section('M', (16, 35), '303', 'Ojalvo', (18, 30)),
                             Section('M', (19, 5), '304', 'N/A', (21, 0)),
                             Section('T', (7, 45), '305', 'Carmody', (9, 40)),
                             Section('T', (9, 55), '306', 'Zeng', (11, 50)),
                             Section('T', (12, 5), '307', 'Zeng', (14, 0))]
        self.sampleText2 = """
T,14:25 (321)301        Dhorkah         17:25
T,19:00 (321)302        Dhorkah         22:00
# comment line
W,14:25 (623)301        McDermott       17:25
W,19:00 (623)303        McDermott       22:00
"""
        self.sampleText3 = """
F,8:00  C                               15:00
F,16:00 c 17:00
"""
        self.fname = "103_4320.txt"
        with open(self.fname, 'w') as f:
            print(self.sampleText1, file=f)

    def tearDown(self):
        os.unlink("103_4320.txt")

    def testParseLine(self):
        p1 = parse_line(self.sampleLine1)
        p2 = parse_line(self.sampleLine2)
        p3 = parse_line(self.sampleLine3)
        self.assertEqual(p1, self.s1)
        self.assertEqual(p2, self.s2)
        self.assertEqual(p3, self.s3)

    def testParseAllLines(self):
        p = parse_all_lines(self.sampleText1)
        self.assertEqual(p, self.sampleParse1)

    def testParseFile(self):
        p = parse_file(self.fname)
        self.assertEqual(p, ((103, 4320), self.sampleParse1))

    def testParseAll(self):
        with open(self.fname, 'w+b') as f:
            f.write(bytes(self.sampleText1, 'UTF-8'))
        p = parse_all()
        self.assertEqual(p, { (103, 4320): self.sampleParse1 })


class TestUtil(unittest.TestCase):
    def setUp(self):
        r1 = Rectangle(Point(0,0), Point(10,10))
        r2 = Rectangle(Point(2,2), Point(8,8))
        self.r3 = Rectangle(Point(0,0), Point(0,0))
        self.s = Scene(r1)
        self.s.add(r2) # set canvas

    def testInvalidDay(self):
        self.assertRaises(ValueError, Section, "X", (14,0), "301", "Foo", (16,0))

    def testSectionDisplay(self):
        self.assertEqual("Section('M', (14, 0), '301', 'Foo', (16, 0))",
                         "%s" % Section('M', (14, 0), '301', 'Foo', (16, 0)))

    def testMinutes(self):
        self.assertEqual(minutes(10, self.s), 60/915.0)
        self.assertEqual(minutes(0, self.s), 0)
        self.s.add(self.r3, True) # make zero-height canvas
        self.assertEqual(minutes(500, self.s), 0)

    def testIndexOf(self):
        self.assertIsNone(index_of("cat", ["bird", "dog"]))
        self.assertEqual(0, index_of(5, [5, 4, 2]))

    def testToMin(self):
        self.assertEqual(0, to_min((0, 0)))
        self.assertEqual(120, to_min((2, 0)))

    def testSubTimes(self):
        self.assertEqual(0, sub_times((4,5), (4,5)))

    def testTimeToStr(self):
        self.assertEqual("5:30", time_to_str((17,30)))
        self.assertEqual("12:00", time_to_str((12,0)))
        self.assertEqual("1:00", time_to_str((13,0)))

    def testInches(self):
        self.assertEqual(inches(10), 720)
        self.assertEqual(inches(0), 0)

    def testYTime(self):
        bg = self.s.get_canvas()
        self.assertEqual(bg.max_y, y_time((7,45), self.s))
        self.assertEqual(bg.min_y, y_time((23,00), self.s))
        self.assertEqual(bg.center_y, y_time((15, 22.5), self.s))

    def testXTime(self):
        bg = self.s.get_canvas()
        day = bg.width / 6.0 
        self.assertEqual(1 + bg.min_x, x_time("M", self.s))
        self.assertEqual(2 + bg.min_x, x_time("T", self.s))
        self.assertEqual(bg.center_x,  x_time("W", self.s))
        self.assertEqual(4 + bg.min_x, x_time("R", self.s))
        self.assertEqual(5 + bg.min_x, x_time("F", self.s))

    def testTimeslot(self):
        s1 = Section("M", (7,45), "301", "Foo", (23,0))
        s2 = Section("M", (7,45), "301", "Foo", (7,45))
        t = timeslot(s1, self.s)
        bg = self.s.get_canvas()
        day = bg.width / 6.0
        self.assertTrue(t.contained_in(self.s.get_canvas()))
        self.assertEqual(0, timeslot(s2, self.s).height)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPoint))
    suite.addTest(unittest.makeSuite(TestScene))
    suite.addTest(unittest.makeSuite(TestRectangle))
    suite.addTest(unittest.makeSuite(TestHLine))
    suite.addTest(unittest.makeSuite(TestText))
    suite.addTest(unittest.makeSuite(TestParser))
    suite.addTest(unittest.makeSuite(TestUtil))
    return suite

if __name__ == "__main__": # pragma: no cover
    import sys, os
    unittest.TextTestRunner(verbosity=2).run(suite())
