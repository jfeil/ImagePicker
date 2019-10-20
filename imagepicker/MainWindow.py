import os
from typing import Dict

from PySide2.QtGui import Qt, QPixmap
from PySide2.QtWidgets import QMainWindow, QStyle, QFileDialog, QFrame

from imagepicker.Ui_MainWindow import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setGeometry(QStyle.alignedRect(Qt.LeftToRight,
                                            Qt.AlignCenter,
                                            self.size(),
                                            app.desktop().availableGeometry()))

        self.ui.actionOpenFolder.triggered.connect(self.open_folder)
        self.ui.forward_small.clicked.connect(lambda: self.show_image(self.current_index + 1))
        self.ui.backward_small.clicked.connect(lambda: self.show_image(self.current_index - 1))
        self.ui.forward_big.clicked.connect(lambda: self.show_image(self.current_index + self.ui.step_spin.value()))
        self.ui.backward_big.clicked.connect(lambda: self.show_image(self.current_index - self.ui.step_spin.value()))
        self.ui.select.clicked.connect(self.select_image)

        self.file_list = {}  # type: Dict[str, bool]
        self.selected_images = []
        self.current_index = 0  # type: int
        self.path = ""  # type: str

    def show_image(self, index):
        if index >= len(self.file_list):
            index = len(self.file_list) - 1
        if index < 0:
            index = 0

        self.ui.backward_small.setDisabled(index == 0)
        self.ui.backward_big.setDisabled(index == 0)
        self.ui.forward_small.setDisabled(index == len(self.file_list) - 1)
        self.ui.forward_big.setDisabled(index == len(self.file_list) - 1)

        self.current_index = index
        image = QPixmap(os.path.join(self.path, list(self.file_list.keys())[self.current_index]))
        self.ui.image_label.setPixmap(image)
        self.setWindowTitle(list(self.file_list.keys())[self.current_index])

        self._draw_border()

    def select_image(self):
        self.file_list[list(self.file_list.keys())[self.current_index]] = \
            not self.file_list[list(self.file_list.keys())[self.current_index]]

        self._draw_border()

    def _draw_border(self):
        bool_ = self.file_list[list(self.file_list.keys())[self.current_index]]
        if bool_:
            self.ui.image_label.setFrameStyle(QFrame.Box | QFrame.Plain)
        else:
            self.ui.image_label.setFrameStyle(QFrame.NoFrame)

    def open_folder(self):
        self.current_index = 0
        self.path = None

        dialog = QFileDialog(self)
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        if dialog.exec():
            self.path = dialog.selectedFiles()[0]
        if not self.path:
            return

        self.file_list = {x: False for x in os.listdir(self.path)}
        self.show_image(self.current_index)