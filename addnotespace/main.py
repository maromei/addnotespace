import os
import sys

from pathlib import Path

from PyQt5 import uic
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QLineEdit
)
from PyQt5.QtGui import QIntValidator


UI_FOLDER_PATH = Path(os.getcwd()) / "ui_files"


class MainWindow(QMainWindow):

    margin_top_line_edit: QLineEdit = None
    margin_right_line_edit: QLineEdit = None
    margin_bot_line_edit: QLineEdit = None
    margin_left_line_edit: QLineEdit = None

    bulk_folder_button: QPushButton = None

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        uic.loadUi(UI_FOLDER_PATH / "main_window.ui", self)
        self.setup_margin_form_input()

        self.bulk_folder_button.pressed.connect(self.bulk_folder_button_pressed)

    def bulk_folder_button_pressed(self):
        print("Click")

    def setup_margin_form_input(self):

        only_pos_int_validator = QIntValidator()
        only_pos_int_validator.setBottom(0)

        self.margin_top_line_edit.setValidator(only_pos_int_validator)
        self.margin_right_line_edit.setValidator(only_pos_int_validator)
        self.margin_bot_line_edit.setValidator(only_pos_int_validator)
        self.margin_left_line_edit.setValidator(only_pos_int_validator)


if __name__ == "__main__":

    app = QApplication(sys.argv)

    with open(UI_FOLDER_PATH / "styles.qss", "r") as f:
        app.setStyleSheet(f.read())

    window = MainWindow()
    window.show()

    app.exec_()
