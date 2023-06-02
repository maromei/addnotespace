import os
from pathlib import Path

from addnotespace.defaults import NoteValues
from addnotespace.app_windows import InfoDialog, MarginProgressDialog


def run_bulk(values: NoteValues) -> NoteValues:
    """
    This function does a bulk run with the given values.

    Args:
        values (NoteValues): The configuration for the bulk run

    Returns:
        NoteValues: Should some error be caught, or something is wrong with
            the values, then they will be modified. The modified values are
            returned.
    """

    bulk_folder = Path(values.bulk_folder).absolute()

    if not bulk_folder.exists():
        message = InfoDialog(
            "error", "The bulk folder is no longer available. Please set it again."
        )
        message.exec_()
        values.bulk_folder = ""
        return values

    file_suffix = values.bulk_name_ending
    if file_suffix == "":
        message = InfoDialog("error", "The file ending can not be empty.")
        message.exec_()
        return values

    file_list = []
    out_files = []
    for file in os.listdir(bulk_folder):

        if not file.endswith(".pdf"):
            continue

        out_file_name = file.split(".")
        out_file_name = ".".join(out_file_name[:-1])
        out_file_name = f"{out_file_name}{file_suffix}.pdf"

        file_list.append(str(bulk_folder / file))
        out_files.append(str(bulk_folder / out_file_name))

    if len(file_list) == 0:
        message = InfoDialog(
            "info", f"No PDF File was found in the directory: '{bulk_folder}'"
        )
        message.exec_()
        return values

    progress_dialogue = MarginProgressDialog(
        file_list,
        out_files,
        int(values.margin_top) / 100,
        int(values.margin_right) / 100,
        int(values.margin_bot) / 100,
        int(values.margin_left) / 100,
    )

    progress_dialogue.exec_()

    return values


def run_single(values: NoteValues) -> NoteValues:
    """
    Does a single run with the given values.

    Args:
        values (NoteValues): values for the run

    Returns:
        NoteValues: modified values in case somethign is wrong with the them
    """

    file_name = values.single_file_folder
    file_name_empty = file_name == ""
    file_name = Path(file_name).absolute()

    new_file_name = values.single_file_target_folder
    new_file_name_empty = new_file_name == ""
    new_file_name = Path(new_file_name).absolute()

    if file_name_empty or new_file_name_empty:
        message = InfoDialog("error", "The filenames cannot be empty.")
        message.exec_()
        return values

    file_valid = file_name.exists() and str(file_name).endswith(".pdf")
    if not file_valid:
        message = InfoDialog("error", "The selected file does not exist anymore.")
        message.exec_()
        values.single_file_folder = ""
        return values

    if not new_file_name.parent.exists():
        message = InfoDialog(
            "error",
            "The selected directory for the new file does not exist anymore.",
        )
        message.exec_()
        values.single_file_target_folder = ""
        return values

    progress_dialogue = MarginProgressDialog(
        [
            str(file_name),
        ],
        [
            str(new_file_name),
        ],
        int(values.margin_top) / 100,
        int(values.margin_right) / 100,
        int(values.margin_bot) / 100,
        int(values.margin_left) / 100,
    )

    progress_dialogue.exec_()
