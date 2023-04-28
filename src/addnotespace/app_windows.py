from PyQt5 import uic
from PyQt5.QtWidgets import (
    QMainWindow,
    QPushButton,
    QLineEdit
)
from PyQt5.QtGui import QIntValidator


class MainWindow(QMainWindow):

    margin_top_line_edit: QLineEdit = None
    margin_right_line_edit: QLineEdit = None
    margin_bot_line_edit: QLineEdit = None
    margin_left_line_edit: QLineEdit = None

    bulk_folder_button: QPushButton = None

    def __init__(self, ui_folder_path, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        uic.loadUi(ui_folder_path / "main_window.ui", self)
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
