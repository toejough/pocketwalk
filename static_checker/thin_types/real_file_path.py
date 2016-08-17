"""Factory for real file paths."""


# [ Imports ]
from pathlib import Path
import logging


# [ Logging ]
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# XXX Better doc strings
# XXX add unit tests
# [ API ]
def real_file_path(path_string: str) -> Path:
    """Build an absolute, concrete, existing path to a file."""
    path = Path(path_string)
    if not path.is_absolute():
        path = Path.cwd() / path_string
    if not path.is_file():
        raise FileNotFoundError("Specified path is not a file: {}".format(str(path)))
    return path
