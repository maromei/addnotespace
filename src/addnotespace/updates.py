import requests
from logging import getLogger
from addnotespace import settings


logger = getLogger(__name__)


def get_latest_link() -> str:
    """
    Returns:
        str: Link to the latest release
    """
    return f"https://github.com/{settings.REPOSITORY_NAME}/releases/latest"


def get_latest_api_link() -> str:
    """
    Returns:
        str: Link to the api for the latest release
    """
    return f"https://api.github.com/repos/{settings.REPOSITORY_NAME}/releases/latest"


def get_latest_release_version() -> str | None:
    """
    Returns the latest release via the github API.

    Returns:
        str|None: A string with the version or :code:`None` if the version
            could not be read.
    """

    try:
        response = requests.get(get_latest_api_link())
        response = response.json()
    except Exception as e:
        logger.error(f"Could not read the latest release version:\n{e}")
        return

    release_version = response.get("name")

    if release_version is not None and release_version[0] == "v":
        release_version = release_version[1:]

    return release_version


def is_new_version_available() -> bool:
    """
    Returns:
        bool: Whether a new version is available.
    """

    latest_version = get_latest_release_version()
    # checks for None here if the version could not be read.
    return latest_version != settings.VERSION and latest_version is not None
