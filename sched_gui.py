import sys
import os
from PyQt4 import QtCore, QtGui
from auto_main import Ui_MainWindow
from scheduler import schedule_grid_svg, add_section_svg
from draw import Scene, Rectangle, Point
from sched_parser import parse_line

class MyWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # no sections have been added
        self.sections = list()

        # init the scene and draw the empty schedule
        self.r = Rectangle(Point(0,0), Point(850,500))
        self.s = Scene(self.r)
        self.s = schedule_grid_svg("Untitled", self.s, self.r)

        self.null = open(os.devnull, "w")
        self.refresh_scene()
        
    def on_pushButton_pressed(self):
        sect = parse_line(self.ui.lineEdit.text())
        self.sections.append(sect)
        add_section_svg(sect, self.s, self.r)
        self.refresh_scene()
        self.ui.lineEdit.clear()

    def refresh_scene(self):
        txt = QtCore.QByteArray(self.s.render_svg(self.null))
        self.ui.svgWidget.load(txt)

    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())
