"""Run commands."""


# [ Imports ]
# [ -Python ]
import subprocess
from types import SimpleNamespace
from typing import Sequence
import logging
# [ -Third Party ]
import a_sync


# [ Logging ]
logger = logging.getLogger(__name__)


# [ Helpers ]
# XXX better doc strings
# XXX use asyncio subprocess
# XXX add unit tests
async def run(command: str, args: Sequence[str]) -> SimpleNamespace:
    """Run the command."""
    logger.info("Running command: {} {}".format(command, ' '.join(args)))
    result = await a_sync.run(
        subprocess.run,
        [command, *args],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    return SimpleNamespace(
        success=result.returncode == 0,
        output=str(result.stdout, 'utf-8')
    )
