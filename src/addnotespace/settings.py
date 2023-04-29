import os

from pathlib import Path
from logging import getLogger


logger = getLogger(__name__)

UI_FOLDER_PATH = \
    Path(os.getcwd()) / os.environ.get("UI_FOLDER_PATH", "ui_files")

STYLE_SHEET_PATH = \
    UI_FOLDER_PATH / os.environ.get("STYLE_SHEET_NAME", "styles.qss")

STYLE_TEMPLATE_PATH = \
    UI_FOLDER_PATH / os.environ.get("STYLE_TEMPLATE_NAME", "styles_template.qss")

STYLE_VARIABLE_PATH = \
    UI_FOLDER_PATH / os.environ.get("STYLE_VAR_NAME", "style_variables.json")

REPLACE_STYLE_VARIABLES = os.environ.get("REPLACE_STYLE_VARIABLES", True)
