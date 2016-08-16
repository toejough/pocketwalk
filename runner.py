"""Run commands."""


# [ Imports ]
import subprocess
from types import SimpleNamespace
import logging


# [ Logging ]
logger = logging.getLogger(__name__)


# [ Helpers ]
def run(command, args):
    """Run the command."""
    logger.info("Running command: {}".format(command))
    result = subprocess.run([command, *args])
    return SimpleNamespace(success=result.returncode == 0)
