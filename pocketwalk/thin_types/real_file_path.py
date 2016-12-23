"""Factory for real file paths."""


# [ Imports ]
from pathlib import Path
import logging
from typing import Any


# [ Pyflakes ]
assert Any


# [ Logging ]
logger = logging.getLogger(__name__)


# XXX Better doc strings
# XXX add unit tests
# [ API ]
def real_file_path(path_string: str) -> Path:
    """Build an absolute, concrete, existing path to a file."""
    path = Path(path_string)  # type: Any
    if not path.is_absolute():
        path = Path.cwd() / path_string
    if not path.is_file():
        raise FileNotFoundError("Specified path is not a file: {}".format(str(path)))
    return path
