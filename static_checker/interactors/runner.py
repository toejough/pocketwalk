"""Run commands."""


# [ Imports ]
import subprocess
from types import SimpleNamespace
import logging


# [ Logging ]
logger = logging.getLogger(__name__)


# [ Helpers ]
# XXX mypy freaks out here and backtraces if I type command as a str.
# XXX add unit tests
def run(command, args):  # type: ignore
    """Run the command."""
    logger.info("Running command: {} {}".format(command, ' '.join(args)))
    result = subprocess.run(
        [command, *args],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    return SimpleNamespace(
        success=result.returncode == 0,
        output=result.stdout
    )
