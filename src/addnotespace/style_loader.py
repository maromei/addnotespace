import json

from logging import getLogger

from PyQt5.QtWidgets import QApplication


logger = getLogger(__name__)


def replace_style_variables(
    variable_file: str,
    template_path: str,
    style_sheet_path: str
):
    """
    Reads the file :code:`template_path` and replaces the variables
    found in the :code:`variable_file`.

    Each key in the :code:`variable file` will replace all
    entries with :code:`@key` in the :code:`template_path`.
    The result will be saved into :code:`style_sheet_path`.

    Args:
        variable_file (str): json file with variable definitions
        template_path (str): template style file
        style_sheet_path (str): where to save new style file

    Raises:
        FileNotFoundError: If either the :code:`variable_path` or
            the :code:`style_sheet_path` was not found.
    """

    variables: dict = dict()

    try:
        with open(variable_file, "r") as f:
            variables: dict = json.load(f)
            prepare_variable_dict(variables)
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


def prepare_variable_dict(variables: dict[str, str]):
    """
    Replaces values in the form of :code:`@key` with the
    value corresponding to that key in the variables dictionary.

    Args:
        variables (dict[str, str]): Variable dictionary

    Raises:
        KeyError: If the key was not found.
    """

    for name, value in variables.items():

        if not value.startswith("@"):
            continue

        try:
            variables[name] = variables[value[1:]]
        except KeyError as e:
            logger.error(
                "Tried replaceing variables in stylesheet variable dict. "
                f"Entry '{name}' has the value '{value}', which was not "
                f"found.\n{e}"
            )
            raise e
