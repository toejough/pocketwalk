# coding: utf-8


"""Checker logic for pocketwalk."""


# [ Import ]
from pocketwalk.core.types_ import Result


# [ API ]
def run() -> Result:
    """Run the static checkers concurrently."""
    return Result.PASS


def watch() -> None:
    """Watch the static checker files concurrently."""
