import os
import json

from pathlib import Path
from logging import getLogger

from __about__ import __version__


logger = getLogger(__name__)

# The parent chaining is due to the frozen file resulting in
# addnotespace/lib/addnotespace/settings.pyc.
# This parent chaining just so happens to also correspond to the
# dev directory structure.
BASE_PATH = Path(__file__).parent.parent.parent

UI_FOLDER_PATH = BASE_PATH / os.environ.get("UI_FOLDER_PATH", "ui_files")

STYLE_SHEET_PATH = UI_FOLDER_PATH / os.environ.get("STYLE_SHEET_NAME", "styles.qss")

STYLE_TEMPLATE_PATH = UI_FOLDER_PATH / os.environ.get(
    "STYLE_TEMPLATE_NAME", "styles_template.qss"
)

STYLE_VARIABLE_PATH = UI_FOLDER_PATH / os.environ.get(
    "STYLE_VAR_NAME", "style_variables.json"
)

REPLACE_STYLE_VARIABLES = os.environ.get("REPLACE_STYLE_VARIABLES", False)

MAIN_WINDOW_UI_PATH = UI_FOLDER_PATH / os.environ.get(
    "MAIN_WINDOW_UI_FILE_NAME", "main_window.ui"
)

INFO_DIALOGUE_UI_PATH = UI_FOLDER_PATH / os.environ.get(
    "INFO_DIALOGUE_UI_NAME", "info_dialogue.ui"
)

PROGRESS_DIALOGUE_UI_PATH = UI_FOLDER_PATH / os.environ.get(
    "PROGRESS_DIALOGUE_UI_NAME", "progress_dialogue.ui"
)

FOLDER_ICON_PATH = UI_FOLDER_PATH / os.environ.get(
    "FOLDER_ICON_NAME", "folder_icon.png"
)

APP_ICON_PATH = UI_FOLDER_PATH / os.environ.get("APP_ICON_NAME", "addnotespace.ico")

DEFAULT_PATH = BASE_PATH / os.environ.get("DEFAULT_PATH", "defaults.json")

VERSION = __version__

REPOSITORY_NAME = os.environ.get("REPOSITORY_NAME", "maromei/addnotespace")

with open(STYLE_VARIABLE_PATH, "r") as f:
    STYLE_VARIABLES = json.load(f)
