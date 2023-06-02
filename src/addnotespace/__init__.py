import os

from logging import getLogger

from dotenv import load_dotenv, find_dotenv


logger = getLogger(__name__)


DOTENV_PATH = os.environ.get("DOTENV_PATH", None)
if DOTENV_PATH is not None:

    path = find_dotenv(DOTENV_PATH)

    if path != "":
        load_dotenv(DOTENV_PATH, verbose=True)
        logger.info(f"Succesfully loaded dotenv file from '{path}'")
    else:
        logger.warning(f"Unable to find dotenv file at '{path}'")

else:
    logger.info(f"'DOTENV_PATH' was not set in the environment.")
