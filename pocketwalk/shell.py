#! /usr/bin/env python
# coding: utf-8


"""Pocketwalk."""


# [ Imports ]
from . import plugger


# [ API ]
# This is a shell class - it's going to have the interfaces to a lot of methods
class Shell:  # pylint: disable=too-many-public-methods
    """Shell around pocketwalk core."""

    # [ API ]
    async def update_vcs(self, config, *, tool_state):
        """Handle version control actions."""
        raise NotImplementedError

    async def get_tool_state(self):
        """Get the tool state."""
        raise NotImplementedError

    def vcs_running(self):
        """Return whether or not the vcs is running."""
        raise NotImplementedError

    def cancelled(self):
        """Return whether or not the application has been cancelled."""
        raise NotImplementedError

    def all_tools_passed(self, tools):
        """Return whether all of the tools have passed."""
        raise NotImplementedError

    def any_tools_not_done(self):
        """Return whether any of the tools are not done."""
        raise NotImplementedError

    def return_codes(self, tools):
        """Return the return codes."""
        raise NotImplementedError

    async def ensure_tools_running(self, contexts_for_tools, *, on_completion):
        """
        Ensure the tools are running with their current contexts.

        Calls the on_completion function with the tool and RC on completion of each tool.
        Runs the tools concurrently.
        """
        raise NotImplementedError

    async def get_tools_failing_preconditions(self, contexts, *, tools_to_run):
        """Get the tools which are failing their preconditions."""
        raise NotImplementedError

    async def filter_out_reported_tools(self, tools_with_contexts):
        """Filter out any previously reported tools."""
        raise NotImplementedError

    async def ensure_stale_tools_stopped(self, contexts_for_tools):
        """
        Ensure the tools are stopped.

        Stops the given tools if their contexts are stale.
        """
        raise NotImplementedError

    async def ensure_tools_stopped(self, contexts_for_tools, *, reason):
        """Ensure the tools are stopped."""
        raise NotImplementedError

    async def ensure_removed_tools_stopped(self, config):
        """Ensure tools not in the tools list are stopped."""
        raise NotImplementedError

    def replay_previous_results_for(self, tools):
        """Replay the previous results for the given tools."""
        raise NotImplementedError

    async def save_context(self, tool, *, context):
        """Save the tool's context."""
        raise NotImplementedError

    async def loop_forever(self):
        """Return whether to loop forever."""
        raise NotImplementedError

    def loop_till_pass(self):
        """Return whether to loop till passing."""
        raise NotImplementedError

    def get_config(self):
        """Get the run config."""
        raise NotImplementedError

    def get_tools_unchanged_since_last_results(self, contexts):
        """Get the tools whose contexts are unchanged since the last results."""
        raise NotImplementedError

    def get_tools_changed_since_last_save(self, contexts):
        """Get the tools whose contexts have changed since the last save."""
        raise NotImplementedError

    async def get_tool_context_data(self, config):
        """Get tool context data."""
        raise NotImplementedError

    def contexts_in_a_and_not_b(self, *, a_context, b_context):
        """Return the contexts in a and not in b."""
        raise NotImplementedError

    @plugger.multi
    async def cleanup(self):
        """Ensure the tools are stopped."""
        raise NotImplementedError

    def get_tools(self, config):
        """Get the tools from the config."""
        raise NotImplementedError
