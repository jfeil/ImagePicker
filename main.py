import sys
from PySide2 import QtWidgets
from imagepicker.MainWindow import MainWindow

app = QtWidgets.QApplication(sys.argv)
main = MainWindow(app)
main.show()
app.exec_()
