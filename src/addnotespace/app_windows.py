import os
from pathlib import Path
from logging import getLogger
from typing import Union

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

        self.setWindowIcon(QIcon(str(settings.APP_ICON_PATH)))

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

    #####################
    ### RUN FUNCTIONS ###
    #####################

    def run_bulk(self):
        """
        Does a bulk run with the given values.
        """

        values = self.create_note_values()

        errors = self.clean_and_validate_bulk_run(values)
        for error in errors:
            error.exec_()

        if len(errors) > 0:
            return

        try:
            run_bulk(values)
        except Exception as e:
            message = (
                "Something went wrong when trying to do a bulk run.\n"
                f"The following error message was raised:\n{e}"
            )
            logger.error(message)
            info_dialogue = InfoDialog("error", message)
            info_dialogue.exec_()

        # If something went wrong with the values and it was caught,
        # the run_bulk() function modifies / resets the values.
        # That is why we apply them again.

        self.write_values_to_fields(values)

    def run_single(self):
        """
        Does a single run.
        """

        values = self.create_note_values(use_single_folder_parents=False)

        errors = self.clean_and_validate_single_run(values)
        for error in errors:
            error.exec_()

        if len(errors) > 0:
            return

        try:
            run_single(values)
        except Exception as e:
            message = (
                "Something went wrong when trying to do a single run.\n"
                f"The following error message was raised:\n{e}"
            )
            logger.error(message)
            info_dialogue = InfoDialog("error", message)
            info_dialogue.exec_()

        # If something went wrong with the values and it was caught,
        # the run_bulk() function modifies / resets the values.
        # That is why we apply them again.

        self.write_values_to_fields(values)

    ###################
    ### OPEN DIOLOG ###
    ###################

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

        The new file name will also be set to
        :code:`single_folder_new_name_line_edit`. The selected path
        will be chosen + the bulk file suffix.
        """

        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select File", self.defaults.single_file_folder, "PDFs (*.pdf)"
        )

        if file_name == "":
            return

        self.single_folder_line_edit.setText(file_name)

        file_suffix = self.bulk_ending_line_edit.text().strip()
        if file_suffix == "":
            file_suffix = "_notes"

        out_file_name = Path(file_name).absolute()
        out_file_name = str(out_file_name).split(".")
        out_file_name = ".".join(out_file_name[:-1])
        out_file_name = f"{out_file_name}{file_suffix}.pdf"

        self.single_new_name_line_edit.setText(out_file_name)

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

        self.single_new_name_line_edit.setText(file_name)

    ##################
    ### VALIDATION ###
    ##################

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
        errors = []

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

    def validate_margin_values(self, values: NoteValues) -> Union["InfoDialog", None]:
        """
        Checks whether the margin values are integers greater than 0.

        Args:
            values (NoteValues): Values to check

        Returns:
            InfoDialog or None: If :code:`None` no errors where found.
                Otherwise the InfoDialog with the error message is returned.
        """

        def is_correct(val: int) -> bool:
            return val >= 0 and type(val) is int

        is_good = is_correct(values.margin_top)
        is_good = is_good and is_correct(values.margin_right)
        is_good = is_good and is_correct(values.margin_bot)
        is_good = is_good and is_correct(values.margin_left)

        if is_good:
            return

        message = (
            "Please check the validity of the margin value. "
            "They need to be integers greater than 0."
        )

        error = InfoDialog("error", message)
        return error

    def clean_and_validate_single_run(
        self, values: NoteValues
    ) -> list["InfoDialog"] | None:
        """
        Given a set of :code:`NoteValues` for a single run, the values
        will be cleaned inplace and potential errors will be returned.

        Args:
            values (NoteValues): Values to be checked.

        Returns:
            list[InfoDialog]: A list of errors.
        """

        errors = []

        margin_error = self.validate_margin_values(values)
        if margin_error is not None:
            errors.append(margin_error)

        file_name = values.single_file_folder
        new_file_name = values.single_file_target_folder

        # is curr pdf?
        if not file_name.endswith(".pdf"):
            message = f"The selected file '{file_name}' is not a valid PDF file."
            errors.append(InfoDialog("error", message))

        # does curr exist?
        if not Path(file_name).exists():
            message = f"The file '{file_name}' does not exist."
            errors.append(InfoDialog("error", message))

        # is name pdf?
        if not new_file_name.endswith(".pdf"):
            new_file_name += ".pdf"
            values.single_file_target_folder = new_file_name

        # does new folder exist?
        if not Path(new_file_name).parent.exists():
            message = "The folder for the new file does not exist."
            errors.append(InfoDialog("error", message))

        return errors

    def clean_and_validate_bulk_run(
        self, values: NoteValues
    ) -> list["InfoDialog"] | None:
        """
        Given a set of :code:`NoteValues` for a bulk run, the values
        will be cleaned inplace and potential errors will be returned.

        Args:
            values (NoteValues): Values to be checked.

        Returns:
            list[InfoDialog]: A list of errors.
        """

        errors = []

        margin_error = self.validate_margin_values(values)
        if margin_error is not None:
            errors.append(margin_error)

        folder = values.bulk_folder
        ending = values.bulk_name_ending

        # does folder exist?
        if not Path(folder).exists():
            message = f"The bulk folder '{folder}' does not exist."
            errors.append(InfoDialog("error", message))

        # is ending not empty?
        ending = ending.strip()
        values.bulk_name_ending = ending
        if ending == "":
            message = f"The bulk file ending cannot be empty."
            errors.append(InfoDialog("error", message))

        return errors

    ##########################
    ### DEFAULTS - NOTESET ###
    ##########################

    def load_defaults(self):
        """
        Loads the default values from the default file and
        places the values into the corresponding fields.
        """

        self.defaults = load_defaults(settings.DEFAULT_PATH)
        self.validate_and_modify_defaults(self.defaults)
        self.write_values_to_fields(self.defaults)

    def save_defaults(self):
        """
        Reads all settings and dumps it into a the defaults file.
        """

        default_values = self.create_note_values()
        self.defaults = default_values
        dump_defaults(default_values, settings.DEFAULT_PATH)
        self.write_values_to_fields(self.defaults)

        message = InfoDialog("success", "Defaults were successfully saved.")
        message.exec_()

    def create_note_values(self, use_single_folder_parents: bool = True) -> NoteValues:
        """
        Creates a :py:class:`addnotespace.defaults.NoteValues` object
        containing the settings currently entered in the GUI.

        Args:
            use_single_folder_parents (bool): Defaults to True.
                If True, only the folder in the single_folder_lines will
                be used. If False, the entire fill will be added aswell.

        Returns:
            NoteValues: The set of values
        """

        single_file_folder = Path(self.single_folder_line_edit.text())
        if use_single_folder_parents:
            single_file_folder = str(single_file_folder.parent.absolute())
        else:
            single_file_folder = str(single_file_folder.absolute())

        single_file_target_folder = Path(self.single_new_name_line_edit.text())

        if use_single_folder_parents:
            single_file_target_folder = str(single_file_target_folder.parent.absolute())
        else:
            single_file_target_folder = str(single_file_target_folder.absolute())

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

    def write_values_to_fields(self, values: NoteValues):
        """
        Takes the :code:`values` and writes them to the corresponding
        fields.

        Args:
            values (NoteValues): values to write to fields
        """

        self.margin_top_line_edit.setText(str(values.margin_top))
        self.margin_right_line_edit.setText(str(values.margin_right))
        self.margin_bot_line_edit.setText(str(values.margin_bot))
        self.margin_left_line_edit.setText(str(values.margin_left))

        self.bulk_folder_line_edit.setText(values.bulk_folder)
        self.bulk_ending_line_edit.setText(values.bulk_name_ending)

        self.single_folder_line_edit.setPlaceholderText(values.single_file_folder)
        self.single_new_name_line_edit.setPlaceholderText(
            values.single_file_target_folder
        )

    ####################
    ### VISUAL SETUP ###
    ####################

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


def run_bulk(values: NoteValues):
    """
    This function does a bulk run with the given values.
    If no PDF FIle was found, the corresponding error will be displayed.

    Args:
        values (NoteValues): The configuration for the bulk run
    """

    bulk_folder = Path(values.bulk_folder).absolute()
    file_suffix = values.bulk_name_ending

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

    progress_dialogue = MarginProgressDialog(
        file_list,
        out_files,
        int(values.margin_top) / 100,
        int(values.margin_right) / 100,
        int(values.margin_bot) / 100,
        int(values.margin_left) / 100,
    )

    progress_dialogue.exec_()


def run_single(values: NoteValues):
    """
    Does a single run with the given values.

    Args:
        values (NoteValues): values for the run
    """

    file_name = Path(values.single_file_folder).absolute()
    new_file_name = Path(values.single_file_target_folder).absolute()

    progress_dialogue = MarginProgressDialog(
        [
            str(file_name),
        ],
        [
            str(new_file_name),
        ],
        int(values.margin_top) / 100,
        int(values.margin_right) / 100,
        int(values.margin_bot) / 100,
        int(values.margin_left) / 100,
    )

    progress_dialogue.exec_()


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
