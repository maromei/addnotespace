from pathlib import Path

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLineEdit, QFileDialog
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

    bulk_run_button: QPushButton = None
    single_run_button: QPushButton = None

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

        self.bulk_run_button.pressed.connect(self.run_bulk)
        self.single_run_button.pressed.connect(self.run_single)

    def run_bulk(self):
        pass  # TODO

    def run_single(self):
        pass  # TODO

    def open_bulk_folder_select(self):
        """
        Opens a :code:`QFileDialog` to select a directory for the bulk run
        directory.
        """

        dir_name = QFileDialog.getExistingDirectory(
            self, "Select Bulk Directory", self.defaults.bulk_folder
        )

        if dir_name == "":
            return

        self.bulk_folder_line_edit.setText(dir_name)

    def open_file_select(self):
        """
        Opens a :code:`QFileDialog` to select a single PDF file.
        The full path to that file is put into the
        :code:`single_folder_line_edit` field.
        """

        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select File", self.defaults.single_file_folder, "PDFs (*.pdf)"
        )

        if file_name == "":
            return

        self.single_folder_line_edit.setText(file_name)

    def open_new_file_location_select(self):
        """
        Opens a :code:`QFileDialog` to select a new file name for the
        new file.
        """

        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Set new File Name",
            self.defaults.single_file_target_folder,
            "PDFs (*.pdf)",
        )

        if file_name == "":
            return

        file_name = self.validate_and_modify_new_file_name(file_name)
        self.single_new_name_line_edit.setText(file_name)

    def validate_and_modify_new_file_name(self, file_name: str) -> str:
        """
        Checks whether the new file name ends with :code:`.pdf` and
        sets the file ending accordingly.

        Args:
            file_name (str):

        Returns:
            str: modified file name

        Raises:
            ValueError: If the parent directory of the file does not exist.
        """

        if not file_name.endswith(".pdf"):
            file_name = f"{file_name}.pdf"

        parent_dir = Path(file_name).parent
        if not parent_dir.exists():
            raise ValueError(
                f"Could not save the file '{Path(file_name).absolute()}'.\n"
                f"The directory '{parent_dir}' does not exist."
            )

        return file_name

    def validate_and_modify_defaults(self, defaults: DefaultValues) -> bool:
        """
        Checks the paths in the default values and sets them to an empty string
        if the directory does not exist.

        Args:
            defaults (DefaultValues):

        Returns:
            bool: True if nothing was changed. False otherwise.
        """

        all_good = True

        if not Path(defaults.single_file_folder).exists():
            defaults.single_file_folder = ""
            all_good = False

        if not Path(defaults.single_file_target_folder).exists():
            self.defaults.single_file_target_folder = ""
            all_good = False

        if not Path(defaults.bulk_folder).exists():
            defaults.bulk_folder = ""
            all_good = False

        return all_good

    def load_defaults(self):
        """
        Loads the default values from the default file and
        places the values into the corresponding fields.
        """

        self.defaults = load_defaults(settings.DEFAULT_PATH)
        self.validate_and_modify_defaults(self.defaults)
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

        self.validate_and_modify_defaults(default_values)
        self.defaults = default_values
        dump_defaults(default_values, settings.DEFAULT_PATH)
        self.write_defaults_to_fields()

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
