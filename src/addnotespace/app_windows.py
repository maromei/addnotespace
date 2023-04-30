from pathlib import Path

from PyQt5 import uic
from PyQt5.QtWidgets import (
    QMainWindow,
    QPushButton,
    QLineEdit
)
from PyQt5.QtGui import QIntValidator, QIcon
from PyQt5.QtCore import QSize


class MainWindow(QMainWindow):

    folder_icon_size = 30

    margin_top_line_edit: QLineEdit = None
    margin_right_line_edit: QLineEdit = None
    margin_bot_line_edit: QLineEdit = None
    margin_left_line_edit: QLineEdit = None

    bulk_folder_button: QPushButton = None
    single_folder_button: QPushButton = None
    single_new_name_button: QPushButton = None

    bulk_folder_button: QPushButton = None


    def __init__(
        self,
        main_window_ui_file_path: str|Path,
        folder_icon_path: str|Path,
        *args,
        **kwargs
    ):
        super(MainWindow, self).__init__(*args, **kwargs)

        uic.loadUi(main_window_ui_file_path, self)
        self.setup_margin_form_input()
        self.setup_folder_button_icons(folder_icon_path)

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


    def setup_folder_button_icons(self, icon_path):

        icon_size = QSize(self.folder_icon_size, self.folder_icon_size)

        self.single_folder_button.setIcon(QIcon(icon_path))
        self.single_folder_button.setIconSize(icon_size)

        self.bulk_folder_button.setIcon(QIcon(icon_path))
        self.bulk_folder_button.setIconSize(icon_size)

        self.single_new_name_button.setIcon(QIcon(icon_path))
        self.single_new_name_button.setIconSize(icon_size)
