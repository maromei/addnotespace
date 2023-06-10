from pathlib import Path
from logging import getLogger
from typing import TYPE_CHECKING

from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtGui import QDropEvent
from PyQt5.QtCore import QUrl

# The import is only used for a type hint.
# However, this already triggers a circular import.
# For this the import should only be done if tools like mypy are TYPE_CHECKING.
# It will be False at run-time.
if TYPE_CHECKING:
    from addnotespace.app_windows import MainWindow


logger = getLogger(__name__)


class DragLineEdit(QLineEdit):
    """
    You can drag files to this QLineEdit and the file path will
    be set as text.

    It is assumed that the LineEdit is enabled.
    """

    def __init__(self, *args, **kwargs):
        super(DragLineEdit, self).__init__(*args, **kwargs)
        """
        Initialize a DragLineEdit
        """

        self.setDragEnabled(True)
        self.setReadOnly(True)

    def dragEnterEvent(self, event: QDropEvent):
        """
        Accepts drags when they contain urls

        Args:
            event (QDropEvent): Drag Event
        """

        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        """
        Sets the given event as text

        Args:
            event (QDropEvent): Drag Event
        """

        file_path: QUrl = self.get_drop_file_path(event)
        self.setText(file_path)

    def get_drop_file_path(self, event: QDropEvent) -> str:
        """
        Gets the full file path from the drag event

        Args:
            event (QDropEvent): drag event

        Returns:
            str: absolute file path
        """

        file_path: QUrl = event.mimeData().urls()[-1]
        file_path = file_path.path()

        return file_path


class DragLineEditSingle(DragLineEdit):
    """
    A drag line edit specifically for the single run.
    """

    main_window: "MainWindow" = None  #: reference to the main window

    def dropEvent(self, event: QDropEvent):
        """
        Sets the url from the dropped file to the text field.
        If the :code:`main_window` is not :code:`None`, the
        :py:meth:`addnotespace.app_windows.MainWindow.auto_set_single_new_file`
        function will be called.

        Args:
            event (QDropEvent): drag event
        """

        file_path: QUrl = self.get_drop_file_path(event)
        self.setText(file_path)

        if self.main_window is not None:
            self.main_window.auto_set_single_new_file(file_path)


class DragLineEditBulk(DragLineEdit):
    """
    A drag line edit specifically for the bulk folder.
    """

    def dropEvent(self, event: QDropEvent):
        """
        Gets the folder from the dragged file and sets it as text.
        If the dragged url is a directory, it will be set directly.

        Args:
            event (QDropEvent):
        """

        file_path: QUrl = self.get_drop_file_path(event)
        file_path: Path = Path(file_path).absolute()

        folder = str(file_path)
        if file_path.is_file():
            folder = str(file_path.parent)

        self.setText(folder)
