import os
import sys
from pathlib import Path
from logging import getLogger

from PyQt5 import uic
from PyQt5.QtWidgets import (
    QMainWindow,
    QPushButton,
    QLineEdit,
    QFileDialog,
    QDialog,
    QLabel,
    QLayout,
    QProgressBar,
)
from PyQt5.QtGui import QIntValidator, QIcon
from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal

from addnotespace import settings, pdf
from addnotespace.defaults import NoteValues, load_defaults, dump_defaults


logger = getLogger(__name__)


class MainWindow(QMainWindow):

    defaults: NoteValues = None

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

        bulk_folder = self.bulk_folder_line_edit.text()
        bulk_folder = Path(bulk_folder).absolute()

        if not bulk_folder.exists():
            message = InfoDialog(
                "error", "The bulk folder is no longer available. Please set it again."
            )
            message.exec_()
            self.bulk_folder_line_edit.setText("")
            return

        file_suffix = self.bulk_ending_line_edit.text()
        if file_suffix == "":
            message = InfoDialog("error", "The file ending can not be empty.")
            message.exec_()
            return

        file_list = []
        out_files = []
        for file in os.listdir(bulk_folder):

            if not file.endswith(".pdf"):
                continue

            out_file_name = file.split(".")
            out_file_name = ".".join(out_file_name[:-1])
            out_file_name = f"{out_file_name}{file_suffix}.pdf"

            file_list.append(str(bulk_folder / file))
            out_files.append(str(bulk_folder / out_file_name))

        if len(file_list) == 0:
            message = InfoDialog(
                "info", f"No PDF File was found in the directory: '{bulk_folder}'"
            )
            message.exec_()
            return

        progress_dialogue = MarginProgressDialog(
            file_list,
            out_files,
            int(self.margin_top_line_edit.text()) / 100,
            int(self.margin_right_line_edit.text()) / 100,
            int(self.margin_bot_line_edit.text()) / 100,
            int(self.margin_left_line_edit.text()) / 100,
        )

        progress_dialogue.exec_()

    def run_single(self):

        file_name = self.single_folder_line_edit.text()
        file_name_empty = file_name == ""
        file_name = Path(file_name).absolute()

        new_file_name = self.single_new_name_line_edit.text()
        new_file_name_empty = new_file_name == ""
        new_file_name = Path(new_file_name).absolute()

        if file_name_empty or new_file_name_empty:
            message = InfoDialog("error", "The filenames cannot be empty.")
            message.exec_()
            return

        file_valid = file_name.exists() and str(file_name).endswith(".pdf")
        if not file_valid:
            message = InfoDialog("error", "The selected file does not exist anymore.")
            message.exec_()
            self.single_folder_line_edit.setText("")
            return

        if not new_file_name.parent.exists():
            message = InfoDialog(
                "error",
                "The selected directory for the new file does not exist anymore.",
            )
            message.exec_()
            self.single_new_name_line_edit.setText("")
            return

        progress_dialogue = MarginProgressDialog(
            [
                str(file_name),
            ],
            [
                str(new_file_name),
            ],
            int(self.margin_top_line_edit.text()) / 100,
            int(self.margin_right_line_edit.text()) / 100,
            int(self.margin_bot_line_edit.text()) / 100,
            int(self.margin_left_line_edit.text()) / 100,
        )

        progress_dialogue.exec_()

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

    def validate_and_modify_defaults(self, defaults: NoteValues) -> bool:
        """
        Checks the paths in the default values and sets them to an empty string
        if the directory does not exist.

        Args:
            defaults (NoteValues):

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

        default_values = self.create_note_values()
        self.defaults = default_values
        dump_defaults(default_values, settings.DEFAULT_PATH)
        self.write_defaults_to_fields()

        message = InfoDialog("success", "Defaults were successfully saved.")
        message.exec_()

    def create_note_values(self) -> NoteValues:
        """
        Creates a :py:class:`addnotespace.defaults.NoteValues` object
        containing the settings currently entered in the GUI.

        Returns:
            NoteValues: The set of values
        """

        single_file_folder = Path(self.single_folder_line_edit.text())
        single_file_folder = str(single_file_folder.parent.absolute())

        single_file_target_folder = Path(self.single_new_name_line_edit.text())
        single_file_target_folder = str(single_file_target_folder.parent.absolute())

        bulk_folder = Path(self.bulk_folder_line_edit.text())
        bulk_folder = str(bulk_folder.absolute())

        note_values = NoteValues(
            margin_top=int(self.margin_top_line_edit.text()),
            margin_right=int(self.margin_right_line_edit.text()),
            margin_bot=int(self.margin_bot_line_edit.text()),
            margin_left=int(self.margin_left_line_edit.text()),
            bulk_folder=bulk_folder,
            bulk_name_ending=self.bulk_ending_line_edit.text(),
            single_file_folder=single_file_folder,
            single_file_target_folder=single_file_target_folder,
        )

        self.validate_and_modify_defaults(note_values)

        return note_values

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


class InfoDialog(QDialog):

    MESSAGE_TYPE_DISPLAY_MAP = {
        "info": "Info:",
        "warning": "Warning:",
        "error": "ERROR:",
    }

    error_type: QLabel = None
    error_text: QLabel = None

    ok_button: QPushButton = None

    def __init__(self, message_type: str, message: str, *args, **kwargs):
        super(InfoDialog, self).__init__(*args, **kwargs)

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

        if message_type not in self.MESSAGE_TYPE_DISPLAY_MAP.keys():
            message_type = "info"
            logger.warning(
                "The Info Dialog was created with an "
                f"invalid message type: '{message_type}'. "
                "Switched back to type 'info'."
            )

        self.setProperty("message_type", message_type)

        uic.loadUi(settings.INFO_DIALOGUE_UI_PATH, self)
        self.ok_button.pressed.connect(self.close)

        self.error_type.setText(self.MESSAGE_TYPE_DISPLAY_MAP[message_type])
        self.error_text.setText(message)

        layout: QLayout = self.layout()
        layout.setSizeConstraint(QLayout.SetFixedSize)


class MarginProgressDialog(QDialog):

    finish_button: QPushButton
    progress_bar: QProgressBar
    progress_text: QLabel

    def __init__(
        self,
        in_paths: list[str],
        out_paths: list[str],
        top_mod: float,
        right_mod: float,
        bot_mod: float,
        left_mod: float,
        *args,
        **kwargs,
    ):
        super(MarginProgressDialog, self).__init__(*args, **kwargs)

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        uic.loadUi(settings.PROGRESS_DIALOGUE_UI_PATH, self)

        self.finish_button.pressed.connect(self.close)

        self.margin_thread = AddMarginThread(
            in_paths, out_paths, top_mod, right_mod, bot_mod, left_mod
        )

        self.margin_thread.progress_signal.connect(self.update_progress_bar)
        self.margin_thread.progress_text_signal.connect(self.update_working_on_text)
        self.margin_thread.start()

    def update_progress_bar(self, progress_value: int):

        if progress_value == -1:
            progress_value = 100
            self.finish()

        self.progress_bar.setValue(progress_value)

    def update_working_on_text(self, display_text: str):

        self.progress_text.setText(display_text)

    def finish(self):

        self.finish_button.setText("Close")
        self.finish_button.setEnabled(True)


class AddMarginThread(QThread):

    progress_signal = pyqtSignal(int)
    progress_text_signal = pyqtSignal(str)

    def __init__(
        self,
        in_paths: list[str],
        out_paths: list[str],
        top_mod: float,
        right_mod: float,
        bot_mod: float,
        left_mod: float,
        *args,
        **kwargs,
    ):
        super(AddMarginThread, self).__init__(*args, **kwargs)

        self.in_paths = in_paths
        self.out_paths = out_paths
        self.top_mod = top_mod
        self.right_mod = right_mod
        self.bot_mod = bot_mod
        self.left_mod = left_mod

    def run(self):

        for i in range(len(self.in_paths)):

            display_path = self.in_paths[i].split("/")[-1]
            display_path = f"Working on: {display_path} ({i+1}/{len(self.in_paths)})"

            self.progress_text_signal.emit(display_path)

            pdf.add_margin(
                self.in_paths[i],
                self.out_paths[i],
                self.top_mod,
                self.right_mod,
                self.bot_mod,
                self.left_mod,
            )

            percentage = (i + 1) / len(self.in_paths) * 100
            self.progress_signal.emit(int(percentage))

        self.progress_signal.emit(-1)
        self.progress_text_signal.emit(f"Finished all {len(self.in_paths)} PDFs")
