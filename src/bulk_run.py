import sys
import logging.config

from logger_config import LOGGING_CONFIG
from initilialize import create_log_dir

create_log_dir()
logging.config.dictConfig(LOGGING_CONFIG)

from PyQt5.QtWidgets import QApplication

from addnotespace import settings, style_loader
from addnotespace.defaults import load_defaults
from addnotespace.app_windows import run_bulk, InfoDialog

logger = logging.getLogger(__name__)

if __name__ == "__main__":

    app = QApplication(sys.argv)
    style_loader.load_styles(app, settings.STYLE_SHEET_PATH)

    values = load_defaults(settings.DEFAULT_PATH)
    try:
        # The run_bulk function creates the window
        values = run_bulk(values)
    except Exception as e:
        message = (
            "Something went wrong when trying to do a bulk run.\n"
            f"The following error message was raised:\n{e}"
        )
        logger.error(message)
        info_dialogue = InfoDialog("error", message)
        info_dialogue.exec_()
