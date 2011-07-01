from draw import *
import unittest

class TestRectangle(unittest.TestCase):
    def setUp(self):
        self.r = Rectangle(Point(0,0), Point(10,10))

    def testRender(self):
        self.assertEqual(self.r.render(), ["% BOX at (0, 0) 10 by 10",
                                           "0 0 moveto",
                                           "10 0 rlineto",
                                           "0 10 rlineto",
                                           "-10 10 rlineto",
                                           "0 -10 rlineto",
                                           "closepath stroke"])
    def testColorRender(self):
        self.r.fill_color(0.5)
        self.assertEqual(self.r.render(), ["% BOX at (0, 0) 10 by 10",
                                           "0 0 moveto",
                                           "10 0 rlineto",
                                           "0 10 rlineto",
                                           "-10 10 rlineto",
                                           "0 -10 rlineto",
                                           "gsave closepath",
                                           "0.50 setgray",
                                           "fill",
                                           "0 setgray grestore"])

class TestHLine(unittest.TestCase):
    def setUp(self):
        self.h = HLine(Point(0,0), 5)

    def testRepr(self):
        self.assertEqual("%s" % self.h, "Horizontal((0, 0), width:5)")

    def testRender(self):
        self.assertEqual(self.h.render(), ["% BOX at (0, 0) 5 by 0",
                                           "0 0 moveto",
                                           "5 0 rlineto",
                                           "0 0 rlineto",
                                           "-5 0 rlineto",
                                           "0 0 rlineto",
                                           "closepath stroke"])

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRectangle))
    suite.addTest(unittest.makeSuite(TestHLine))
    return suite

if __name__ == "__main__":
    import sys, os
    sys.stdout = open(os.devnull, "w") # suppress output
    unittest.TextTestRunner(verbosity=2).run(suite())
