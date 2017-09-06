#! /usr/bin/env python
# coding: utf-8


"""Pocketwalk context manager."""


# XXX rename this - context managers are an established thing in python, and this is not that.
# [ Imports ]
import abc


# [ Internal ]
class ContextManager(abc.ABC):
    """Context manager plugin for pocketwalk."""

    # [ API ]
    @abc.abstractmethod
    def get_tools_unchanged_since_last_results(self, contexts):
        """Get the tools whose contexts are unchanged since the last results."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_tools_changed_since_last_save(self, contexts):
        """Get the tools whose contexts have changed since the last save."""
        raise NotImplementedError

    @abc.abstractmethod
    async def get_tool_context_data(self, config):
        """Get tool context data."""
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def contexts_in_a_and_not_b(*, a_context, b_context):
        """Return the contexts in a and not in b."""
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    async def save_context(tool, *, context):
        """Save the current context for the given tool."""
        raise NotImplementedError
