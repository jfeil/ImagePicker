import enum
import os
from collections import OrderedDict
from enum import Enum, auto, IntEnum
from os import remove
from shutil import copy2, move
from typing import Dict

from PySide2.QtGui import Qt, QPixmap, QImageReader
from PySide2.QtWidgets import QMainWindow, QStyle, QFileDialog, QFrame

from imagepicker.Ui_MainWindow import Ui_ImagePicker


class SelectionStatus(IntEnum):
    UNSELECTED = 0
    SELECTED = 1


class ModificationType(Enum):
    COPY = auto()
    MOVE = auto()
    REMOVE = auto()


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()

        self.ui = Ui_ImagePicker()
        self.title = "ImagePicker"
        self.ui.setupUi(self)
        self.setGeometry(QStyle.alignedRect(Qt.LeftToRight,
                                            Qt.AlignCenter,
                                            self.size(),
                                            app.desktop().availableGeometry()))

        self.ui.actionOpenFolder.triggered.connect(lambda: self.open_folder())
        self.ui.forward_small.clicked.connect(lambda: self.show_image(self.current_index + 1))
        self.ui.backward_small.clicked.connect(lambda: self.show_image(self.current_index - 1))
        self.ui.forward_big.clicked.connect(lambda: self.show_image(self.current_index + self.ui.step_spin.value()))
        self.ui.backward_big.clicked.connect(lambda: self.show_image(self.current_index - self.ui.step_spin.value()))
        self.ui.select.clicked.connect(self.select_image)

        self.ui.actionCopy_Selected.triggered.connect(lambda: self.modify_items(SelectionStatus.SELECTED, ModificationType.COPY))
        self.ui.actionCopy_Unselected.triggered.connect(lambda: self.modify_items(SelectionStatus.UNSELECTED, ModificationType.COPY))
        self.ui.actionMove_Unselected.triggered.connect(lambda: self.modify_items(SelectionStatus.UNSELECTED, ModificationType.MOVE))
        self.ui.actionRemove_Selected.triggered.connect(lambda: self.modify_items(SelectionStatus.SELECTED, ModificationType.REMOVE))
        self.ui.actionMove_Selected.triggered.connect(lambda: self.modify_items(SelectionStatus.SELECTED, ModificationType.MOVE))
        self.ui.actionRemove_Unselected.triggered.connect(lambda: self.modify_items(SelectionStatus.UNSELECTED, ModificationType.REMOVE))

        self.file_list = {}  # type: Dict[str, bool]
        self.selected_images = []
        self.current_index = 0  # type: int
        self.path = ""  # type: str

    def show_image(self, index):
        if len(self.file_list) == 0:
            self.ui.image_label.setText("No images available.")
            return

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
        self.setWindowTitle("{} - {}".format(self.title, list(self.file_list.keys())[self.current_index]))

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

    def open_folder(self, path=None):
        self.current_index = 0
        self.path = path
        if path is None:

            dialog = QFileDialog(self)
            dialog.setAcceptMode(QFileDialog.AcceptOpen)
            dialog.setFileMode(QFileDialog.DirectoryOnly)
            if dialog.exec():
                self.path = dialog.selectedFiles()[0]
            if not self.path:
                return

        list_ = os.listdir(self.path)
        list_ = sorted(list_)
        self.file_list = OrderedDict()
        for item in list_:
            if item.split(".")[-1] in QImageReader.supportedImageFormats():
                self.file_list[item] = False

        self.show_image(self.current_index)

    def modify_items(self, selection_status: SelectionStatus, modify_type: ModificationType):
        item_list = []
        for key, value in self.file_list.items():
            if value == selection_status:
                item_list.append(key)

        def select_new_folder():
            dialog = QFileDialog(self)
            dialog.setAcceptMode(QFileDialog.AcceptSave)
            dialog.setFileMode(QFileDialog.DirectoryOnly)
            if dialog.exec():
                return dialog.selectedFiles()[0]

        if modify_type == ModificationType.COPY:
            save_path = select_new_folder()
            for file in item_list:
                copy2(os.path.join(self.path, file), save_path)

        elif modify_type == ModificationType.MOVE:
            save_path = select_new_folder()
            for file in item_list:
                move(os.path.join(self.path, file), save_path)
            self.open_folder(self.path)

        elif modify_type == ModificationType.REMOVE:
            for file in item_list:
                remove(os.path.join(self.path, file))
            self.open_folder(self.path)

        else:
            raise ValueError("{} is wrong.".format(modify_type))
