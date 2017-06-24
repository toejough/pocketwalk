# coding: utf-8


"""Commit logic for pocketwalk."""


# [ Import ]
import enum


# [ API ]
class Result(enum.Enum):
    """Result enums."""

    COMMITTED = enum.auto()


def run() -> Result:
    """Run a commit."""
    raise NotImplementedError  # pragma: no cover
