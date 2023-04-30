from pathlib import Path

from PyQt5 import uic
from PyQt5.QtWidgets import (
    QMainWindow,
    QPushButton,
    QLineEdit
)
from PyQt5.QtGui import QIntValidator, QIcon
from PyQt5.QtCore import QSize

from addnotespace import settings
from addnotespace.defaults import DefaultValues, load_defaults, dump_defaults


class MainWindow(QMainWindow):

    defaults: DefaultValues = None

    folder_icon_size = 30

    margin_top_line_edit: QLineEdit = None
    margin_right_line_edit: QLineEdit = None
    margin_bot_line_edit: QLineEdit = None
    margin_left_line_edit: QLineEdit = None

    bulk_folder_button: QPushButton = None
    single_folder_button: QPushButton = None
    single_new_name_button: QPushButton = None

    bulk_folder_line_edit: QLineEdit = None
    bulk_ending_line_edit: QLineEdit = None
    single_folder_line_edit: QLineEdit = None
    single_new_name_line_edit: QLineEdit = None

    default_loader_load_button: QPushButton = None
    default_loader_save_button: QPushButton = None


    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        ################
        ### UI SETUP ###
        ################

        uic.loadUi(settings.MAIN_WINDOW_UI_PATH, self)
        self.setup_margin_form_input()
        self.setup_folder_button_icons(str(settings.FOLDER_ICON_PATH))

        ################
        ### DEFAULTS ###
        ################

        self.load_defaults()

        ####################
        ### ACTION SETUP ###
        ####################

        self.bulk_folder_button.pressed.connect(self.open_bulk_folder_select)
        self.single_folder_button.pressed.connect(self.open_file_select)
        self.single_new_name_button.pressed.connect(self.open_new_file_location_select)

        self.default_loader_load_button.pressed.connect(self.load_defaults)
        self.default_loader_save_button.pressed.connect(self.save_defaults)

    def open_bulk_folder_select(self):
        pass


    def open_file_select(self):
        pass


    def open_new_file_location_select(self):
        pass


    def load_defaults(self):
        """
        Loads the default values from the default file and
        places the values into the corresponding fields.
        """

        self.defaults = load_defaults(settings.DEFAULT_PATH)
        self.write_defaults_to_fields()


    def save_defaults(self):
        """
        Reads all settings and dumps it into a the defaults file.
        """

        single_file_folder = Path(self.single_folder_line_edit.text())
        single_file_folder = str(single_file_folder.parent.absolute())

        single_file_target_folder = Path(self.single_new_name_line_edit.text())
        single_file_target_folder = str(single_file_target_folder.parent.absolute())

        bulk_folder = Path(self.bulk_folder_line_edit.text())
        bulk_folder = str(bulk_folder.absolute())

        default_values = DefaultValues(
            margin_top=int(self.margin_top_line_edit.text()),
            margin_right=int(self.margin_right_line_edit.text()),
            margin_bot=int(self.margin_bot_line_edit.text()),
            margin_left=int(self.margin_left_line_edit.text()),
            bulk_folder=bulk_folder,
            bulk_name_ending=self.bulk_ending_line_edit.text(),
            single_file_folder=single_file_folder,
            single_file_target_folder=single_file_target_folder,
        )

        dump_defaults(default_values, settings.DEFAULT_PATH)


    def setup_margin_form_input(self):
        """
        Sets up the Validators for the margin form inputs.
        """

        only_pos_int_validator = QIntValidator()
        only_pos_int_validator.setBottom(0)

        self.margin_top_line_edit.setValidator(only_pos_int_validator)
        self.margin_right_line_edit.setValidator(only_pos_int_validator)
        self.margin_bot_line_edit.setValidator(only_pos_int_validator)
        self.margin_left_line_edit.setValidator(only_pos_int_validator)


    def setup_folder_button_icons(self, icon_path: str):
        """
        Sets the folder icon for the file dialogue buttons and sets its
        size with the :code:`MainWindow.folder_icon_size`.

        Args:
            icon_path (str): Path to the icon to use.
        """

        icon_size = QSize(self.folder_icon_size, self.folder_icon_size)

        self.single_folder_button.setIcon(QIcon(icon_path))
        self.single_folder_button.setIconSize(icon_size)

        self.bulk_folder_button.setIcon(QIcon(icon_path))
        self.bulk_folder_button.setIconSize(icon_size)

        self.single_new_name_button.setIcon(QIcon(icon_path))
        self.single_new_name_button.setIconSize(icon_size)


    def write_defaults_to_fields(self):
        """
        Takes the :code:`self.defaults` and writes them to the corresponding
        fields.
        """

        self.margin_top_line_edit.setText(str(self.defaults.margin_top))
        self.margin_right_line_edit.setText(str(self.defaults.margin_right))
        self.margin_bot_line_edit.setText(str(self.defaults.margin_bot))
        self.margin_left_line_edit.setText(str(self.defaults.margin_left))

        self.bulk_folder_line_edit.setText(self.defaults.bulk_folder)
        self.bulk_ending_line_edit.setText(self.defaults.bulk_name_ending)

        self.single_folder_line_edit.setPlaceholderText(
            self.defaults.single_file_folder
        )
        self.single_new_name_line_edit.setPlaceholderText(
            self.defaults.single_file_target_folder
        )
