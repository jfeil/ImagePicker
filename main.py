import os
import sys
from PySide2 import QtWidgets
from imagepicker.MainWindow import MainWindow

app = QtWidgets.QApplication(sys.argv)

path = None
if len(sys.argv) >= 2 and os.path.isdir(sys.argv[1]):
    path = sys.argv[1]

main = MainWindow(app, path)
main.show()
app.exec_()
