#! /usr/bin/env python
# coding: utf-8


"""Pocketwalk tool runner interface."""


# [ Imports ]
import abc


# [ API ]
class ToolRunner(abc.ABC):
    """Tool Runner Plugin."""

    @abc.abstractmethod
    def __init__(self):
        """Init the state."""
        raise NotImplementedError

    # [ API ]
    @abc.abstractmethod
    async def get_tool_state(self):
        """Get the tool state."""
        raise NotImplementedError

    @abc.abstractmethod
    def all_tools_passed(self, tools):
        """Return whether all of the tools have passed."""
        raise NotImplementedError

    @abc.abstractmethod
    def any_tools_not_done(self):
        """Return whether any of the tools are not done."""
        raise NotImplementedError

    @abc.abstractmethod
    async def return_codes(self, tools):
        """Return the return codes."""
        raise NotImplementedError

    @abc.abstractmethod
    async def ensure_tools_running(self, contexts_for_tools, *, on_completion):
        """
        Ensure the tools are running with their current contexts.

        Calls the on_completion function with the tool and RC on completion of each tool.
        Runs the tools concurrently.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_tools_failing_preconditions(self, contexts, *, tools_to_run):
        """Get the tools which are failing their preconditions."""
        raise NotImplementedError

    @abc.abstractmethod
    async def filter_out_reported_tools(self, tools_with_contexts):
        """Filter out any previously reported tools."""
        raise NotImplementedError

    @abc.abstractmethod
    async def cleanup(self):
        """Ensure the tools are stopped."""
        raise NotImplementedError

    @abc.abstractmethod
    async def ensure_stale_tools_stopped(self, contexts_for_tools):
        """
        Ensure the tools are stopped.

        Stops the given tools if their contexts are stale.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def ensure_tools_stopped(self, contexts_for_tools, *, reason):
        """Ensure the tools are stopped."""
        raise NotImplementedError

    @abc.abstractmethod
    async def ensure_removed_tools_stopped(self, config):
        """Ensure tools not in the tools list are stopped."""
        raise NotImplementedError

    @abc.abstractmethod
    async def replay_previous_results_for(self, tools):
        """Replay the previous results for the given tools."""
        raise NotImplementedError
