#! /usr/bin/env python
# coding: utf-8


"""Pocketwalk vcs interface."""


# [ Imports ]
import abc


# [ API ]
class VCS(abc.ABC):
    """VCS plugin for the pocketwalk shell."""

    @abc.abstractmethod
    def __init__(self):
        """Init the state."""
        raise NotImplementedError

    # [ API ]
    @abc.abstractmethod
    async def update_vcs(self, config, *, tool_state):
        """Handle version control actions."""
        raise NotImplementedError

    @abc.abstractmethod
    def vcs_running(self):
        """Return whether or not vcs is running."""
        raise NotImplementedError

    @abc.abstractmethod
    async def cleanup(self):
        """Clean up a running vcs future."""
        raise NotImplementedError
