import argparse
from pathlib import Path
from addnotespace.app_windows import MainWindow, run_single, run_bulk


def setup_arg_parser() -> argparse.ArgumentParser:
    """
    Creates the argument parser and returns it.
    Nothing will be parsed yet!

    Returns:
        argparse.ArgumentParser:
    """

    parser = argparse.ArgumentParser(
        "addnotespace", description="Add white space to your pdf files."
    )

    parser.add_argument("-f", "--file", help="Specify a file to add margins to.")

    parser.add_argument(
        "-d",
        "--directory",
        help="A directory where whitespace gets added to each file.",
    )

    parser.add_argument(
        "-bs",
        "--bulk-suffix",
        help="The suffix added to each newly created file name in a bulk run.",
    )

    parser.add_argument(
        "-o", "--output", help="The output file name for a single file run."
    )

    parser.add_argument(
        "-t",
        "--top",
        action="store",
        type=int,
        help="Percentage of how much whitespace to add to the top of the pdf.",
    )

    parser.add_argument(
        "-r",
        "--right",
        action="store",
        type=int,
        help="Percentage of how much whitespace to add to the right of the pdf.",
    )

    parser.add_argument(
        "-b",
        "--bot",
        action="store",
        type=int,
        help="Percentage of how much whitespace to add to the bottom of the pdf.",
    )

    parser.add_argument(
        "-l",
        "--left",
        action="store",
        type=int,
        help="Percentage of how much whitespace to add to the left of the pdf.",
    )

    return parser


def should_cli_run(args: argparse.Namespace) -> bool:
    """
    Args:
        args (argparse.Namespace): The parsed cli arguments

    Returns:
        bool: Wether the CLI should be run instead of the GUI.
    """
    return args.file is not None or args.directory is not None


def run_cli_job(args: argparse.Namespace, main_window: MainWindow):
    """
    Runs the CLI Job.

    Args:
        args (argparse.Namespace): The parsed CLI argumetns
        main_window (MainWindow): The main_window, which will not be shown.
    """

    ################
    ### Get args ###
    ################

    arg_dic = vars(args)
    arg_dic = {k: v for k, v in arg_dic.items() if v is not None}

    ####################
    ### build values ###
    ####################

    values = main_window.defaults

    values.margin_top = arg_dic.get("top", values.margin_top)
    values.margin_right = arg_dic.get("right", values.margin_right)
    values.margin_bot = arg_dic.get("bot", values.margin_bot)
    values.margin_left = arg_dic.get("top", values.margin_left)

    if arg_dic.get("file") is not None:
        path = Path(arg_dic.get("file")).resolve()
        values.single_file_folder = str(path)

    if arg_dic.get("directory") is not None:
        path = Path(arg_dic.get("directory")).resolve()
        values.bulk_folder = str(path)

    values.single_file_target_folder = arg_dic.get(
        "output", values.single_file_target_folder
    )
    values.bulk_name_ending = arg_dic.get("bulk_suffix", values.bulk_name_ending)

    ##############
    ### Errors ###
    ##############

    is_single_run = arg_dic.get("file") is not None

    if is_single_run:
        errors = main_window.clean_and_validate_single_run(values)
    else:
        errors = main_window.clean_and_validate_bulk_run(values)

    if len(errors) > 0:
        print(
            "### ERROR ###\n"
            "Encountered the following errors while trying to "
            "process the request:\n"
        )
        for i, error in enumerate(errors):
            print(f"{i}: {error.error_text.text()}")

        print("\nExiting...")
        return

    ###########
    ### Run ###
    ###########

    if is_single_run:
        run_single(values, is_gui=False)
    else:
        run_bulk(values, is_gui=False)
