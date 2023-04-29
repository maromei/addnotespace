import os
import sys

from pathlib import Path

from PyQt5.QtWidgets import QApplication

from addnotespace.app_windows import MainWindow
from addnotespace import settings, style_loader


if __name__ == "__main__":

    app = QApplication(sys.argv)

    if settings.REPLACE_STYLE_VARIABLES:
        style_loader.replace_style_variables(
            settings.STYLE_VARIABLE_PATH,
            settings.STYLE_TEMPLATE_PATH,
            settings.STYLE_SHEET_PATH
        )

    style_loader.load_styles(
        app,
        settings.STYLE_SHEET_PATH
    )

    window = MainWindow(settings.UI_FOLDER_PATH)
    window.show()

    app.exec_()
