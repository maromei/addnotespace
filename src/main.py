import sys
import logging.config

from logger_config import LOGGING_CONFIG
from initilialize import create_log_dir

create_log_dir()
logging.config.dictConfig(LOGGING_CONFIG)

from PyQt5.QtWidgets import QApplication

from addnotespace.app_windows import MainWindow
from addnotespace import settings, style_loader, cli


if __name__ == "__main__":

    parser = cli.setup_arg_parser()
    args = parser.parse_args()

    app = QApplication(sys.argv)

    if settings.REPLACE_STYLE_VARIABLES:
        style_loader.replace_style_variables(
            settings.STYLE_VARIABLE_PATH,
            settings.STYLE_TEMPLATE_PATH,
            settings.STYLE_SHEET_PATH,
        )

    style_loader.load_styles(app, settings.STYLE_SHEET_PATH)

    window = MainWindow()

    if cli.should_cli_run(args):
        cli.run_cli_job(args, window)
    else:
        window.show()
        app.exec_()
