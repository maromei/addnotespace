import json

from logging import getLogger

from PyQt5.QtWidgets import QApplication


logger = getLogger(__name__)


def replace_style_variables(
    variable_file: str,
    template_path: str,
    style_sheet_path: str
):

    variables: dict = dict()

    try:
        with open(variable_file, "r") as f:
            variables: dict = json.load(f)
    except FileNotFoundError as e:
        logger.error(
            "Could not replace style variables as the "
            f"variable file '{variable_file}' does not exist.\n{e}"
        )
        raise e

    style_content: str = ""
    try:
        with open(template_path, "r") as f:
            style_content: str = f.read()
    except FileNotFoundError as e:
        logger.error(
            "Could not replace style variables as the "
            f"style sheet '{template_path}' does not exist.\n{e}"
        )
        raise e

    for name, value in variables.items():
        style_content = style_content.replace(f"@{name}", value)

    with open(style_sheet_path, "w+") as f:
        f.write(style_content)


def load_styles(app: QApplication, style_file_path: str):

    try:
        with open(style_file_path, "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError as e:
        logger.error(
            f"Could not load the style sheet '{style_file_path}'.\n"
            f"{e}"
        )
        raise e
