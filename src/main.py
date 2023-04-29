import os
import sys

from pathlib import Path

from PyQt5.QtWidgets import QApplication

from addnotespace.app_windows import MainWindow
from addnotespace import settings


if __name__ == "__main__":

    app = QApplication(sys.argv)

    with open(settings.UI_FOLDER_PATH / "styles.qss", "r") as f:
        app.setStyleSheet(f.read())

    window = MainWindow(settings.UI_FOLDER_PATH)
    window.show()

    app.exec_()
