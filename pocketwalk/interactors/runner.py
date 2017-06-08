# coding: utf-8


"""Run commands."""


# [ Imports ]
# [ -Python ]
import asyncio
import concurrent.futures
import subprocess
from types import SimpleNamespace
from typing import Sequence


# [ Helpers ]
async def run(command: str, args: Sequence[str]) -> SimpleNamespace:
    """Run the command."""
    process = await asyncio.create_subprocess_exec(
        command, *args,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    try:
        await process.wait()
    except concurrent.futures.CancelledError:
        process.terminate()
        try:
            await asyncio.wait_for(process.wait(), timeout=3)
        # mypy says no such error
        except asyncio.TimeoutError:  # type: ignore
            process.kill()
            try:
                await asyncio.wait_for(process.wait(), timeout=3)
            # mypy says no such error
            except asyncio.TimeoutError:  # type: ignore
                raise RuntimeError("subprocess for {command} did not stop after terminate and kill commands.".format(**locals()))
        raise
    return SimpleNamespace(
        success=process.returncode == 0,
        output=str(await process.stdout.read(), 'utf-8'),
    )
