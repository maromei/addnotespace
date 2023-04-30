import json
from pathlib import Path
from logging import getLogger
from dataclasses import dataclass


logger = getLogger(__name__)


@dataclass
class DefaultValues:
    """
    Contains all default values which can be entered into the GUI.
    """

    margin_top: int = 0 #:
    margin_right: int = 0 #:
    margin_bot: int = 0 #:
    margin_left: int = 0 #:

    bulk_folder: str = "" #:
    bulk_name_ending: str = "" #:

    single_file_folder: str = "" #:
    single_file_target_folder: str = "" #:


def load_defaults(file_path:str|Path) -> DefaultValues:
    """
    Loads the default values from the :code:`file_path`

    Args:
        file_path (str | Path): path to the json containing the default values

    Returns:
        DefaultValues:
    """

    try:
        with open(file_path, "r") as f:
            default_dic = json.load(f)
    except FileNotFoundError:
        default_dic = dict()

    default_values = DefaultValues(**default_dic)

    return default_values


def dump_defaults(default_values: DefaultValues, file_path:str|Path):
    """
    Dumps the default values to the given :code:`file_path`

    Args:
        default_values (DefaultValues):
        file_path (str | Path):
    """

    default_dict: dict = default_values.__dict__
    with open(file_path, "w+") as f:
        json.dump(default_dict, f, indent=4)
