"""Run commands."""


# [ Imports ]
# [ -Python ]
import subprocess
from types import SimpleNamespace
from typing import Sequence
import asyncio
import logging
import concurrent.futures


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
    # XXX way too much nesting here
    try:
        await process.wait()
    except concurrent.futures.CancelledError:
        process.terminate()
        try:
            await asyncio.wait_for(process.wait(), timeout=3)
        # XXX mypy says no such error
        except asyncio.TimeoutError:  # type: ignore
            process.kill()
            try:
                await asyncio.wait_for(process.wait(), timeout=3)
            # XXX mypy says no such error
            except asyncio.TimeoutError:  # type: ignore
                raise RuntimeError("subprocess for {} did not stop after terminate and kill commands.".format(command))
        raise
    return SimpleNamespace(
        success=process.returncode == 0,
        output=str(await process.stdout.read(), 'utf-8')
    )
