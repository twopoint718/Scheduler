import sys
import os
from PyQt4 import QtCore, QtGui
from auto_main import Ui_MainWindow
from scheduler import schedule_grid_svg, add_section_svg
from draw import Scene, Rectangle, Point
from sched_parser import parse_line
from sched_util import Section

class MyWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # init the scene and draw the empty schedule
        self.title = "Untitled"
        self.r = Rectangle(Point(0,0), Point(850,500))
        self.s = Scene(self.r)
        self.s = schedule_grid_svg(self.title, self.s, self.r)
        self.numobjects = 0
        self.min_objects = len(self.s.objects)

        self.null = open(os.devnull, "w")
        self.refresh_scene()
        
    def on_pushButton_pressed(self):
        title = self.ui.schedule_title.text()
        if not self.title == title:
            self.title = title
            # title has changed, save current objects and make new scene
            if self.numobjects > 0:
                from_end = self.numobjects * -1
                added_objects = self.s.objects[from_end:]
            else:
                added_objects = list()
            self.r = Rectangle(Point(0,0), Point(850,500))
            self.s = Scene(self.r)
            self.s = schedule_grid_svg(title, self.s, self.r)
            self.s.objects.extend(added_objects)
            self.numobjects = len(added_objects)

        day = list("MTWRF")[self.ui.day.currentIndex()]
        start = self.ui.start_time.time()
        start_h = start.hour()
        start_m = start.minute()
        end = self.ui.end_time.time()
        end_h = end.hour()
        end_m = end.minute()
        ta = self.ui.ta_name.text()
        section = self.ui.section_number.value()

        sect = Section(day, (start_h, start_m), section, ta, (end_h, end_m))
        add_section_svg(sect, self.s, self.r)
        self.numobjects += 1
        self.refresh_scene()

    def on_undoButton_pressed(self):
        if len(self.s.objects) > self.min_objects:
            self.s.objects.pop()
            self.refresh_scene()

    def refresh_scene(self):
        txt = QtCore.QByteArray(self.s.render_svg(self.null))
        self.ui.svgWidget.load(txt)

    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())
