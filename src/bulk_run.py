import sys
import logging.config

from logger_config import LOGGING_CONFIG
from initilialize import create_log_dir

create_log_dir()
logging.config.dictConfig(LOGGING_CONFIG)

from PyQt5.QtWidgets import QApplication

from addnotespace import settings, style_loader
from addnotespace.app_windows import InfoDialog, MainWindow

logger = logging.getLogger(__name__)


def run():

    app = QApplication(sys.argv)
    style_loader.load_styles(app, settings.STYLE_SHEET_PATH)

    main_window = MainWindow()

    try:
        # The run_bulk function creates the window
        main_window.run_bulk()
    except Exception as e:
        message = (
            "Something went wrong when trying to do a bulk run.\n"
            f"The following error message was raised:\n{e}"
        )
        logger.error(message)
        info_dialogue = InfoDialog("error", message)
        info_dialogue.exec_()


if __name__ == "__main__":

    try:
        run()
    except Exception as e:
        logger.error(f"Error in Bulk-Run: {e}")
        raise e
