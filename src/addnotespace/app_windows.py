import sys
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
    QButtonGroup,
)
from PyQt5.QtGui import QIntValidator, QIcon
from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal

from addnotespace import settings, pdf, updates
from addnotespace.defaults import NoteValues, load_defaults, dump_defaults
from addnotespace.widgets import DragLineEditBulk, DragLineEditSingle, PreviewSketch


logger = getLogger(__name__)


class MainWindow(QMainWindow):
    """
    The main window containing all the default functionality.
    """

    defaults: NoteValues = None

    folder_icon_size = 30

    margin_top_line_edit: QLineEdit = None
    margin_right_line_edit: QLineEdit = None
    margin_bot_line_edit: QLineEdit = None
    margin_left_line_edit: QLineEdit = None

    bulk_folder_button: QPushButton = None
    single_folder_button: QPushButton = None
    single_new_name_button: QPushButton = None

    bulk_folder_line_edit: "DragLineEditBulk" = None
    bulk_ending_line_edit: QLineEdit = None
    single_folder_line_edit: "DragLineEditSingle" = None
    single_new_name_line_edit: QLineEdit = None

    default_loader_load_button: QPushButton = None
    default_loader_save_button: QPushButton = None

    bulk_run_button: QPushButton = None
    single_run_button: QPushButton = None

    preview_sketch: "PreviewSketch" = None

    preview_ratio_button_group: QButtonGroup = None

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        ################
        ### UI SETUP ###
        ################

        self.setWindowIcon(QIcon(str(settings.APP_ICON_PATH)))

        uic.loadUi(settings.MAIN_WINDOW_UI_PATH, self)
        self.setup_margin_form_input()
        self.setup_folder_button_icons(str(settings.FOLDER_ICON_PATH))

        self.setWindowTitle(f"AddNoteSpace v{settings.VERSION}")

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

        self.single_folder_line_edit.main_window = self
        self.preview_sketch.main_window = self

        self.margin_top_line_edit.textChanged.connect(self.preview_sketch.update)
        self.margin_right_line_edit.textChanged.connect(self.preview_sketch.update)
        self.margin_bot_line_edit.textChanged.connect(self.preview_sketch.update)
        self.margin_left_line_edit.textChanged.connect(self.preview_sketch.update)

        self.preview_ratio_button_group.buttonClicked.connect(self.update_preview_ratio)

    def update_preview_ratio(self):
        """
        Sets the preview sketches ratio and updates the sketch.
        """

        button = self.preview_ratio_button_group.checkedButton()
        width, height = button.text().split(":")

        self.preview_sketch.slide_ratio_w = int(width)
        self.preview_sketch.slide_ratio_h = int(height)

        self.preview_sketch.update()

    #####################
    ### RUN FUNCTIONS ###
    #####################

    def show(self, *args, **kwargs):
        """
        Overrides the default :code:`show()` method to check for
        a new version and display a dialog for it.
        """

        super(MainWindow, self).show(*args, **kwargs)

        # Checking for updates results in windows recognizing the final
        # program as a virus. --> removed for now
        return

        if not updates.is_new_version_available():
            return

        new_version = updates.get_latest_release_version()

        # The color for the link needs to be hard coded since
        # there is currently no way to set it via qss files.

        link = updates.get_latest_link()
        link = f'<a href="{link}" style="color: #eceff4;">{link}</a>'

        message = (
            f"Version {new_version} is available!<br>"
            "Download the new version at:<br><br>"
            f"{link}"
        )
        dialog = InfoDialog("info", message, enable_rich_text=True)
        dialog.exec_()

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

    def auto_set_single_new_file(self, single_path: str) -> str:
        """
        Automatically sets the new file name for a single path.
        It uses the singel path + the bulk suffix.

        If the bulk suffix is empty, :code:`_notes` will be used instead.

        Args:
            single_path (str): The selected single file path.

        Returns:
            str: The out file name.
        """

        file_suffix = self.bulk_ending_line_edit.text().strip()
        if file_suffix == "":
            file_suffix = "_notes"

        out_file_name = Path(single_path).absolute()
        out_file_name = str(out_file_name).split(".")
        out_file_name = ".".join(out_file_name[:-1])
        out_file_name = f"{out_file_name}{file_suffix}.pdf"

        # windows path conversion. Would work without it, but for
        # consistency of display, it is still done
        if sys.platform == "win32":
            out_file_name = out_file_name.replace("/", "\\")

        self.single_new_name_line_edit.setText(out_file_name)
        return out_file_name

    ###################
    ### OPEN DIOLOG ###
    ###################

    def open_bulk_folder_select(self):
        """
        Opens a :code:`QFileDialog` to select a directory for the bulk run
        directory.

        If the bulk folder input has something in it, then this will be
        the directory where the dialog starts in. Otherwise the
        default will be used.
        """

        open_folder = self.defaults.bulk_folder

        current_bulk_input = self.bulk_folder_line_edit.text()
        if current_bulk_input != "":
            open_folder = current_bulk_input

        dir_name = QFileDialog.getExistingDirectory(
            self, "Select Bulk Directory", open_folder
        )

        if dir_name == "":
            return

        # windows path conversion. Would work without it, but for
        # consistency of display, it is still done
        if sys.platform == "win32":
            dir_name = dir_name.replace("/", "\\")

        self.bulk_folder_line_edit.setText(dir_name)

    def open_file_select(self):
        """
        Opens a :code:`QFileDialog` to select a single PDF file.
        The full path to that file is put into the
        :code:`single_folder_line_edit` field.

        The new file name will also be set to
        :code:`single_folder_new_name_line_edit`. The selected path
        will be chosen + the bulk file suffix.

        The folder will open in the location of the file which is currently
        in the line edit. If the line edit is empty, the default
        folder will be used.
        """

        open_folder = self.defaults.single_file_folder

        current_input = self.single_folder_line_edit.text()
        if current_input != "":
            open_folder = str(Path(current_input).parent)

        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select File", open_folder, "PDFs (*.pdf)"
        )

        if file_name == "":
            return

        # windows path conversion. Would work without it, but for
        # consistency of display, it is still done
        if sys.platform == "win32":
            file_name = file_name.replace("/", "\\")

        self.single_folder_line_edit.setText(file_name)
        self.auto_set_single_new_file(file_name)

    def open_new_file_location_select(self):
        """
        Opens a :code:`QFileDialog` to select a new file name for the
        new file.
        """

        open_folder = self.defaults.single_file_target_folder

        current_input = self.single_folder_line_edit.text()
        current_new_name_input = self.single_new_name_line_edit.text()
        if current_new_name_input != "":
            open_folder = str(Path(current_new_name_input).parent)
        elif current_input != "":
            open_folder = str(Path(current_input).parent)

        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Set new File Name",
            open_folder,
            "PDFs (*.pdf)",
        )

        if file_name == "":
            return

        # windows path conversion. Would work without it, but for
        # consistency of display, it is still done
        if sys.platform == "win32":
            file_name = file_name.replace("/", "\\")

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

        message = InfoDialog("info", "Defaults were successfully saved.")
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

        top = self.margin_top_line_edit.text()
        right = self.margin_right_line_edit.text()
        bot = self.margin_bot_line_edit.text()
        left = self.margin_left_line_edit.text()

        sketch_ratio = self.preview_ratio_button_group.checkedButton().text()

        note_values = NoteValues(
            margin_top=int(top if top != "" else 0),
            margin_right=int(right if right != "" else 0),
            margin_bot=int(bot if bot != "" else 0),
            margin_left=int(left if left != "" else 0),
            bulk_folder=bulk_folder,
            bulk_name_ending=self.bulk_ending_line_edit.text(),
            single_file_folder=single_file_folder,
            single_file_target_folder=single_file_target_folder,
            preview_sketch_ratio=sketch_ratio,
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

        self.check_preview_ratio_button(values.preview_sketch_ratio)

    def check_preview_ratio_button(self, ratio: str):
        """
        Given a ratio string like :code:`4:3`, the right button
        will be checked in the preview ration button group.

        The preview will be updated.

        Args:
            ratio (str): ratio string. f.e. :code:`16:9`
        """

        for button in self.preview_ratio_button_group.buttons():
            if button.text() == ratio:
                button.setChecked(True)

        self.update_preview_ratio()

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


def run_bulk(values: NoteValues, is_gui: bool = True):
    """
    This function does a bulk run with the given values.
    If no PDF FIle was found, the corresponding error will be displayed.

    Args:
        values (NoteValues): The configuration for the bulk run
        is_gui (bool): If True, a GUI for the progress will be displayed.
            Otherwise console output will be generated.
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

        msg_string = f"No PDF File was found in the directory: '{bulk_folder}'"
        message = InfoDialog("info", msg_string)

        if is_gui:
            message.exec_()
        else:
            print(msg_string)
            return

    progress_dialogue = MarginProgressDialog(
        file_list,
        out_files,
        int(values.margin_top) / 100,
        int(values.margin_right) / 100,
        int(values.margin_bot) / 100,
        int(values.margin_left) / 100,
        is_gui=is_gui,
    )

    progress_dialogue.exec_()


def run_single(values: NoteValues, is_gui: bool = True):
    """
    Does a single run with the given values.

    Args:
        values (NoteValues): values for the run
        is_gui (bool): If True, a GUI for the progress will be displayed.
            Otherwise console output will be generated.
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
        is_gui=is_gui,
    )

    progress_dialogue.exec_()


class InfoDialog(QDialog):
    """
    A Dialog displaying simple messages.
    These can have 3 different types.
    "info", "warning" and "error".

    This Dialog has an additional property :code:`message_type` which can
    be used for custom syling in qss files.
    """

    #: Display map for each message type, to how that
    #: type will be displayed.
    MESSAGE_TYPE_DISPLAY_MAP = {
        "info": "Info:",
        "warning": "Warning:",
        "error": "ERROR:",
    }

    error_type: QLabel = None  #:
    error_text: QLabel = None  #:

    ok_button: QPushButton = None  #:

    def __init__(
        self,
        message_type: str,
        message: str,
        enable_rich_text: bool = False,
        *args,
        **kwargs,
    ):
        """
        Creates A message dialog.

        Args:
            message_type (str): Can be either "info", "warning" or "error"
            message (str):
            enable_rich_text (bool): Whether or not to enable rich text formatting
        """

        super(InfoDialog, self).__init__(*args, **kwargs)

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

        if message_type not in self.MESSAGE_TYPE_DISPLAY_MAP.keys():
            logger.warning(
                "The Info Dialog was created with an "
                f"invalid message type: '{message_type}'. "
                "Switched back to type 'info'."
            )
            message_type = "info"

        self.setProperty("message_type", message_type)

        uic.loadUi(settings.INFO_DIALOGUE_UI_PATH, self)
        self.ok_button.pressed.connect(self.close)

        self.error_type.setText(self.MESSAGE_TYPE_DISPLAY_MAP[message_type])
        self.error_text.setText(message)

        layout: QLayout = self.layout()
        layout.setSizeConstraint(QLayout.SetFixedSize)

        if enable_rich_text:
            self.error_text.setTextFormat(Qt.RichText)


class MarginProgressDialog(QDialog):
    """
    The Dialog dispalying the progress of
    working on multiple PDF files.
    """

    finish_button: QPushButton  #:
    progress_bar: QProgressBar  #:
    progress_text: QLabel  #:

    is_gui: bool

    def __init__(
        self,
        in_paths: list[str],
        out_paths: list[str],
        top_mod: float,
        right_mod: float,
        bot_mod: float,
        left_mod: float,
        is_gui: bool = True,
        *args,
        **kwargs,
    ):
        """
        Create a progress dialog while for working on the files.
        The process will automatically be started once this classes
        :code:`exec_()` function is started.

        Args:
            in_paths (list[str]):
            out_paths (list[str]):
            top_mod (float): top mod as fraction
            right_mod (float): right mod as fraction
            bot_mod (float): bot mod as fraction
            left_mod (float): left mod as fraction
            is_gui (bool): If True the progress will be displayed
                as a GUI, otherwise only print statements will be made.
        """
        super(MarginProgressDialog, self).__init__(*args, **kwargs)

        self.is_gui = is_gui

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        uic.loadUi(settings.PROGRESS_DIALOGUE_UI_PATH, self)

        self.finish_button.pressed.connect(self.close)

        self.margin_thread = AddMarginThread(
            in_paths, out_paths, top_mod, right_mod, bot_mod, left_mod
        )

        self.margin_thread.progress_signal.connect(self.update_progress_bar)
        self.margin_thread.progress_text_signal.connect(self.update_working_on_text)

        if is_gui:
            self.margin_thread.start()

    def update_progress_bar(self, progress_value: int):
        """
        Updates the progress bar. If the progress_value hits 100, then
        the process is finished.

        Args:
            progress_value (int):
        """

        if progress_value == -1:
            progress_value = 100
            self.finish()

        self.progress_bar.setValue(progress_value)

    def update_working_on_text(self, display_text: str):
        """
        Sets the progress value to display.
        If :code:`is_gui` is :code:`True` then console output is generated.

        Args:
            display_text (str):
        """

        self.progress_text.setText(display_text)

        if not self.is_gui:
            terminal_size = os.get_terminal_size()
            sys.stdout.write(f"{display_text.ljust(terminal_size.columns, ' ')}\r")

    def finish(self):
        """
        Enables Close button and finishes processes.
        """

        self.finish_button.setText("Close")
        self.finish_button.setEnabled(True)

        if not self.is_gui:
            sys.stdout.flush()
            print("\nDone.")

    def exec_(self) -> int:
        """
        Executes the window.
        If :code:`self.is_gui` is :code:`True`, no GUI window
        will be created, but the thread will still be run.

        Returns:
            int: status code.
        """

        if self.is_gui:
            return super(MarginProgressDialog, self).exec_()

        self.margin_thread.run()
        return 0

    def exec(self) -> int:
        """
        Executes the window.
        If :code:`self.is_gui` is :code:`True`, no GUI window
        will be created, but the thread will still be run.

        Returns:
            int: status code.
        """

        return self.exec_()


class AddMarginThread(QThread):
    """
    A Thread for working multiple PDF files.
    """

    #: signal for transmitting percentage of progress
    progress_signal = pyqtSignal(int)

    #: Sends signal of which PDF it is working on
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
        """
        Thread for adding space on given PDF files.

        Args:
            in_paths (list[str]):
            out_paths (list[str]):
            top_mod (float): top mod as fraction
            right_mod (float): right mod as fraction
            bot_mod (float): bot mod as fraction
            left_mod (float): left mod as fraction
        """
        super(AddMarginThread, self).__init__(*args, **kwargs)

        self.in_paths = in_paths
        self.out_paths = out_paths
        self.top_mod = top_mod
        self.right_mod = right_mod
        self.bot_mod = bot_mod
        self.left_mod = left_mod

    def run(self):
        """
        Runs adding space on multiple pdf files.

        Sends signals with :code:`progress_signal` and
        :code:`progress_text_signal`.
        The :code:`progress_signal` will send -1 if the process is finished.
        """

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
