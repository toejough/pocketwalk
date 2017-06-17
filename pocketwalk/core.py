#! /usr/bin/env python
# coding: utf-8


"""Pocketwalk."""


# [ Imports ]
# [ -Python ]
import sys
# [ -Third Party ]
import runaway
from runaway import signals
from runaway.extras import looping
import wrapt
# [ -Project ]
from .shell import Shell
from .plugger import Plugger


# [ Internal ]
@wrapt.decorator
async def retry(wrapped, _instance, args, kwargs):
    """Retry 3 times."""
    tries = 0
    max_tries = 3
    while True:
        try:
            return await wrapped(*args, **kwargs)
        # purposely broad except here
        except Exception as error:  # pylint: disable=broad-except
            if tries < max_tries:
                tries += 1
                print(f"Got exception {type(error)}: {error}... trying again...")
                await signals.sleep(0.1)
            else:
                raise


# [ API ]
# XXX need per function docs
# XXX need project docs
# XXX need mypy typing

class Core:
    """Pocketwalk core."""

    def __init__(self, this_shell: Shell):
        """Init the state."""
        self._shell = this_shell

    # [ API ]
    async def main(self):
        """Run a single loop."""
        tools = await looping.do_while(
            self._ensure_updated_tools_running,
            self._should_loop,
            [],
        )
        await self._shell.cleanup()
        return max(await self._shell.return_codes(tools), default=0)

    # [ Internal ]
    async def _should_loop(self, tools):
        """Return whether the app should loop."""
        return (
            not await signals.call(self._shell.cancelled) and (
                await signals.call(self._shell.loop_forever) or
                await signals.call(self._shell.vcs_running) or (
                    await signals.call(self._shell.loop_till_pass) and
                    not await signals.call(self._shell.all_tools_passed, tools)
                ) or
                await signals.call(self._shell.any_tools_not_done)
            )
        )

    @retry
    async def _ensure_updated_tools_running(self, _state):
        """Ensure updated tools are running, if any, else wait."""
        # detail - needed to not peg CPU/disk with requests/tasks more frequently than necessary
        await signals.sleep(1)

        # details - needed for sync'd data for starting/stopping/checking tools
        config = await self._shell.get_config()
        context_data = await self._shell.get_tool_context_data(config)

        # tool state ID
        tools_with_changed_contexts = self._shell.get_tools_changed_since_last_save(context_data)
        tools_with_unchanged_contexts = self._shell.get_tools_unchanged_since_last_results(context_data)
        unreported_unchanged_tools = await self._shell.filter_out_reported_tools(tools_with_unchanged_contexts)
        # XXX extend the valid names
        tools_with_failing_preconditions = await self._shell.get_tools_failing_preconditions(context_data, tools_to_run=tools_with_changed_contexts)  # pylint: disable=invalid-name
        tools_to_run = self._shell.contexts_in_a_and_not_b(a_context=tools_with_changed_contexts, b_context=tools_with_failing_preconditions)

        # replay valid results
        await signals.call(self._shell.replay_previous_results_for, unreported_unchanged_tools)

        # starting/stopping tools
        await signals.call(self._shell.ensure_tools_stopped, tools_with_failing_preconditions, reason="failing preconditions")
        await signals.call(self._shell.ensure_stale_tools_stopped, tools_with_changed_contexts)
        await signals.call(self._shell.ensure_tools_stopped, tools_with_unchanged_contexts, reason="reverted files")
        await signals.call(self._shell.ensure_removed_tools_stopped, config)
        await signals.call(self._shell.ensure_tools_running, tools_to_run, on_completion=self._shell.save_context)

        # detail - needed for vcs to determine whether to run/stop
        tool_state = await signals.call(self._shell.get_tool_state)

        # VCS - commit to source control
        await signals.call(self._shell.update_vcs, config, tool_state=tool_state)
        # XXX what about when the VCS fails?  What about when any shell command raises?  There need to be guards in place.
        # need general debug output saved to a file, and return 1

        # detail - need a return state for the outer loop
        return await signals.call(self._shell.get_tools, config)


# [ Main ]
def main():
    """Main."""
    shell = Plugger().implement(Shell(), namespace='pocketwalk')
    core = Core(shell)

    sys.exit(runaway.run(core.main()))
