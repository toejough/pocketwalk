"""Run commands."""


# [ Imports ]
# [ -Python ]
import subprocess
from types import SimpleNamespace
from typing import Sequence
import asyncio
import logging


# [ Logging ]
logger = logging.getLogger(__name__)


# [ Helpers ]
# XXX better doc strings
# XXX add unit tests
async def run(command: str, args: Sequence[str]) -> SimpleNamespace:
    """Run the command."""
    logger.info("Running command: {} {}".format(command, ' '.join(args)))
    process = await asyncio.create_subprocess_exec(
        command, *args,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    await process.wait()
    return SimpleNamespace(
        success=process.returncode == 0,
        output=str(await process.stdout.read(), 'utf-8')
    )
