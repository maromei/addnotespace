"""
This file simply exists as a standalone CLI binary, which is only relevant for
windows. Since we can either build the addnotespace exe as a WIN32GUI base,
which disables all console output, and in fact crashes once output is
generated. Or without a base, but then a console opens.

--> Create this standalone exe for cli jobs.
"""

import sys
import logging.config
from logging import getLogger

from logger_config import LOGGING_CONFIG
from initilialize import create_log_dir

create_log_dir()
logging.config.dictConfig(LOGGING_CONFIG)

from PyQt5.QtWidgets import QApplication

from addnotespace.app_windows import MainWindow
from addnotespace import cli


logger = getLogger(__name__)


def run():

    parser = cli.setup_arg_parser()
    args = parser.parse_args()

    app = QApplication(sys.argv)
    window = MainWindow()
    cli.run_cli_job(args, window)


if __name__ == "__main__":

    try:
        run()
    except Exception as e:
        logger.error(f"Error in Main: {e}")
        raise e
