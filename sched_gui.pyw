import sys
import os
import subprocess

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import PyQt4

from scheduler_auto import Ui_MainWindow
from alert_auto import Ui_Dialog

import scheduler

class Scheduler(QMainWindow):

    format = "%s,%s\t%s\t%s\t%s\n"

    def __init__(self):
        QMainWindow.__init__(self)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # row 1 is in the gui
        self.row = 1
	
    def on_addButton_pressed(self):
        self.ui.tableWidget.insertRow(self.row)
        self.row += 1

    def on_removeButton_pressed(self):
        if self.row <= 0:
            self.row = 0
            return
        self.row -= 1
        self.ui.tableWidget.removeRow(self.row)

    def on_scheduleButton_pressed(self):
        course = self.ui.course.text()
        room = self.ui.room.text()
        if not len(course) == 3:
            w = Alert("Missing required field: Course")
            r = w.exec_()
            return r
        if not len(room) == 4:
            w = Alert("Missing required field: Room")
            r = w.exec_()
            return r

        tw = self.ui.tableWidget
        rows = tw.rowCount()
        data = list()
        for r in range(rows):
            try:
                ta  = tw.item(r,0).text()
                sec = tw.item(r,1).text()
                day = tw.item(r,2).text()
                sta = tw.item(r,3).text()
                end = tw.item(r,4).text()
            except AttributeError:
                Alert("No field can be empty").exec_()
                return
            if not valid_section(sec):
                Alert("'%s' is not a valid number" % sec).exec_()
                return
            if not valid_day(day):
                Alert("'%s' is not a valid day (e.g. M, T, W..)" % day).exec_()
                return
            if not valid_time(sta):
                Alert("'%s' is not a valid time" % sta).exec_()
                return
            if not valid_time(end):
                Alert("'%s' is not a valid time" % end).exec_()
                return
            
            data.append([ta, sec, day, sta, end])

        # now actually write it
        fname = "%s_%s.txt" % (course, room)
        f = open(fname, "w")
        for row in data:
            ta, sec, day, sta, end = row
            f.write(self.format % (day, sta, sec, ta, end))
            sys.stdout.write(self.format % (day, sta, sec, ta, end))
        f.close()
        Alert("File '%s' was written" % fname).exec_()
        subprocess.call(["python", "scheduler.py"])
        

    def on_clearButton_pressed(self):
        self.ui.tableWidget.clearContents()

    def keyPressEvent(self, event):
        if event.key() == 16777220: # enter key
            self.ui.tableWidget.insertRow(self.row)
            self.row += 1

            
class Alert(QDialog):
    def __init__(self, text):
        QDialog.__init__(self)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.label.setText(text)

    def on_okayButton_pressed(self):
        self.accept()


def valid_section(s):
    if s == "c" or s == "C":
        return True
    try:
        x = int(s)
        return True
    except:
        return False


def valid_day(s):
    return s in ["M", "T", "W", "R", "F"]


def valid_time(s):
    try:
        h, m = s.split(":")
        h = int(h)
        m = int(m)
        return h >= 0 and h < 24 and m >= 0 and m < 60
    except:
        return False


def main():
    app = QApplication(sys.argv)
    window = Scheduler()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
