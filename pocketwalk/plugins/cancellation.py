#! /usr/bin/env python
# coding: utf-8


"""Pocketwalk."""


# [ Imports ]
# [ -Python ]
import signal
import sys


# [ API ]
def get_cancellation():
    """Get the cancellation plugin."""
    cancellation = Cancellation()
    cancellation.init()
    return cancellation


# [ Internal ]
class Cancellation:
    """Cancellation plugin."""

    def __init__(self):
        """Init the state."""
        self._cancelled = False

    def init(self):
        """Initialize the shell."""
        signal.signal(signal.SIGINT, lambda _signum, _frame: self._sigint_handler())

    def _sigint_handler(self):
        """
        Handle SIGINT.

        Handle the first incidence of the signal by setting the cancelled flag.

        Any SIGNINT received after the flag has been set will cause an immediate exit.
        """
        if self._cancelled:
            sys.exit("EXITING DUE TO MULTIPLE SIGINTS RECEIVED.")
        self._cancelled = True
        print("\n\nCTRL-C detected.")

    def cancelled(self):
        """Return whether or not the application has been cancelled."""
        return self._cancelled


# [ Vulture ]
assert all((
    get_cancellation,
))
