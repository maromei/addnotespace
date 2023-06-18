import sys
from pathlib import Path
from logging import getLogger
from typing import TYPE_CHECKING

from PyQt5 import QtCore
from PyQt5.QtWidgets import QLineEdit, QWidget
from PyQt5.QtGui import QDropEvent, QPainter, QPen, QBrush, QColor, QPainterPath
from PyQt5.QtCore import QUrl, QRect

from addnotespace import settings

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

        # remove the leading / for windows file paths
        if sys.platform == "win32":
            file_path = file_path[1:]

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


class PreviewSketch(QWidget):
    """
    The widget displays the preview slide with the margins.
    """

    main_window: "MainWindow" = None  #:

    #: fraction of the available space the preview can occupy
    background_slide_mod = 9.5 / 10

    title_left = 1 / 10  #: ratio of slide width as space to the left of the title
    title_top = 1 / 10  #: ratio of slide width as space to the top of the title
    title_width = 8 / 10  #: ratio of slide width as title width
    title_height = 4 / 10  #: ration of slide height as title height

    item_left = 1.2 / 10  #: ratio of slide width as space to the left of the item
    item_space = 3.5 / 10  #: ration of slide as space between title and item
    item_height = 1 / 10  #: ratio of slide width as item width
    item_width = 4 / 10  #: ratio of slide height as item height

    #: ration of available space for the radius of corner rounding
    rounding_mod = 1 / 50

    #: the slide will always have this ratio. this is the width of the ratio
    slide_ratio_w = 16
    #: the slide will always have this ratio. this is the height of the ratio
    slide_ratio_h = 9

    def __init__(self, *args, **kwargs) -> None:
        super(PreviewSketch, self).__init__(*args, **kwargs)

    def paintEvent(self, event):
        """
        Draws the preview.

        Args:
            event (QEvent):
        """

        ###############
        ### Margins ###
        ###############

        margins = self.main_window.create_note_values()

        margins.margin_top /= 100
        margins.margin_right /= 100
        margins.margin_bot /= 100
        margins.margin_left /= 100

        #############
        ### Setup ###
        #############

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()

        background_color = QColor(settings.STYLE_VARIABLES["snow-storm-s1"])
        slide_color = QColor(settings.STYLE_VARIABLES["polar-night-s1"])

        title_color = QColor(settings.STYLE_VARIABLES["aurora-red"])
        item_color = QColor(settings.STYLE_VARIABLES["snow-storm-s1"])

        rounding = rect.width() * self.rounding_mod

        ##################
        ### Rectangles ###
        ##################

        reference_w = 1 + margins.margin_left + margins.margin_right
        reference_w *= self.slide_ratio_w

        reference_h = 1 + margins.margin_top + margins.margin_bot
        reference_h *= self.slide_ratio_h

        reference_ratio = reference_w / reference_h
        rect_ratio = rect.width() / rect.height()

        if reference_w / reference_h < rect_ratio:

            background_h = rect.height() * self.background_slide_mod
            background_w = reference_ratio * background_h

            background_rect = QRect(
                int(rect.left() + (rect.width() - background_w) / 2),
                int(rect.top() + (1 - self.background_slide_mod) / 2 * rect.height()),
                int(background_w),
                int(background_h),
            )

        else:

            background_w = rect.width() * self.background_slide_mod
            background_h = 1 / reference_ratio * background_w

            background_rect = QRect(
                int(rect.left() + (1 - self.background_slide_mod) / 2 * rect.width()),
                int(rect.top() + (rect.height() - background_h) / 2),
                int(background_w),
                int(background_h),
            )

        slide_w = background_rect.width() / (
            1 + margins.margin_left + margins.margin_right
        )
        slide_h = background_rect.height() / (
            1 + margins.margin_top + margins.margin_bot
        )

        slide_rect = QRect(
            int(background_rect.left() + margins.margin_left * slide_w),
            int(background_rect.top() + margins.margin_top * slide_h),
            int(slide_w),
            int(slide_h),
        )

        title_rect = QRect(
            int(slide_rect.left() + slide_rect.width() * self.title_left),
            int(slide_rect.top() + slide_rect.height() * self.title_top),
            int(slide_rect.width() * self.title_width),
            int(slide_rect.height() * self.title_height),
        )

        item_rect = QRect(
            int(slide_rect.left() + slide_rect.width() * self.item_left),
            int(title_rect.top() + title_rect.height() * (1 + self.item_space)),
            int(slide_rect.width() * self.item_width),
            int(slide_rect.height() * self.item_height),
        )

        #############
        ### Paint ###
        #############

        painter.setBrush(QBrush(background_color, QtCore.Qt.SolidPattern))
        painter.drawRoundedRect(background_rect, rounding, rounding)

        painter.setBrush(QBrush(slide_color, QtCore.Qt.SolidPattern))
        painter.drawRoundedRect(slide_rect, rounding, rounding)

        painter.setBrush(QBrush(title_color, QtCore.Qt.SolidPattern))
        painter.drawRoundedRect(title_rect, rounding, rounding)

        painter.setBrush(QBrush(item_color, QtCore.Qt.SolidPattern))
        painter.drawRoundedRect(item_rect, rounding, rounding)
