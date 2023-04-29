import os

from pathlib import Path
from logging import getLogger


logger = getLogger(__name__)

UI_FOLDER_PATH = Path(os.getcwd()) / os.environ.get("UI_FOLDER_PATH", "ui_files")
STYLE_SHEET_PATH = UI_FOLDER_PATH / os.environ.get("STYLE_SHEET_NAME", "styles.qss")

REPLACE_STYLE_VARIABLES = os.environ.get("REPLACE_STYLE_VARIABLES", True)
