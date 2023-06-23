import os
from pathlib import Path


def create_log_dir():
    """
    Creates the directory log if it does not exists yet.
    """

    log_dir = Path(__file__).parent.parent / "logs"

    if not log_dir.exists():
        os.makedirs(log_dir)
