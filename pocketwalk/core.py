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
from .shell import VCS, Config, ToolRunner, ContextManager, Cancellation
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

    def __init__(
        self, *,
        vcs: VCS,
        cancellation: Cancellation,
        config: Config,
        tool_runner: ToolRunner,
        context_manager: ContextManager,
    ):
        """Init the state."""
        self._vcs = vcs
        self._cancellation = cancellation
        self._config = config
        self._tool_runner = tool_runner
        self._context_manager = context_manager

    # [ API ]
    async def main(self):
        """Run a single loop."""
        tools = await looping.do_while(
            self._ensure_updated_tools_running,
            self._should_loop,
            [],
        )
        await self._vcs.cleanup()
        await self._tool_runner.cleanup()
        return max(await self._tool_runner.return_codes(tools), default=0)

    # [ Internal ]
    async def _should_loop(self, tools):
        """Return whether the app should loop."""
        return (
            not await signals.call(self._cancellation.cancelled) and (
                await signals.call(self._config.loop_forever) or
                await signals.call(self._vcs.vcs_running) or (
                    await signals.call(self._config.loop_till_pass) and
                    not await signals.call(self._tool_runner.all_tools_passed, tools)
                ) or
                await signals.call(self._tool_runner.any_tools_not_done)
            )
        )

    @retry
    async def _ensure_updated_tools_running(self, _state):
        """Ensure updated tools are running, if any, else wait."""
        # detail - needed to not peg CPU/disk with requests/tasks more frequently than necessary
        await signals.sleep(1)

        # details - needed for sync'd data for starting/stopping/checking tools
        config = await self._config.get_config()
        context_data = await self._context_manager.get_tool_context_data(config)

        # tool state ID
        tools_with_changed_contexts = self._context_manager.get_tools_changed_since_last_save(context_data)
        tools_with_unchanged_contexts = self._context_manager.get_tools_unchanged_since_last_results(context_data)
        unreported_unchanged_tools = await self._tool_runner.filter_out_reported_tools(tools_with_unchanged_contexts)
        # XXX extend the valid names
        tools_with_failing_preconditions = await self._tool_runner.get_tools_failing_preconditions(  # pylint: disable=invalid-name
            context_data,
            tools_to_run=tools_with_changed_contexts,
        )
        tools_to_run = self._context_manager.contexts_in_a_and_not_b(
            a_context=tools_with_changed_contexts,
            b_context=tools_with_failing_preconditions,
        )

        # replay valid results
        await self._tool_runner.replay_previous_results_for(unreported_unchanged_tools)

        # starting/stopping tools
        await self._tool_runner.ensure_tools_stopped(tools_with_failing_preconditions, reason="failing preconditions")
        await self._tool_runner.ensure_stale_tools_stopped(tools_with_changed_contexts)
        await self._tool_runner.ensure_tools_stopped(tools_with_unchanged_contexts, reason="reverted files")
        await self._tool_runner.ensure_removed_tools_stopped(config)
        await self._tool_runner.ensure_tools_running(tools_to_run, on_completion=self._context_manager.save_context)

        # detail - needed for vcs to determine whether to run/stop
        tool_state = await self._tool_runner.get_tool_state()

        # VCS - commit to source control
        await self._vcs.update_vcs(config, tool_state=tool_state)
        # XXX what about when the VCS fails?  What about when any shell command raises?  There need to be guards in place.
        # need general debug output saved to a file, and return 1

        # detail - need a return state for the outer loop
        return await self._config.get_tools(config)


# [ Main ]
def main():
    """Main."""
    plugger = Plugger('pocketwalk')
    core = Core(
        vcs=plugger.resolve(VCS),
        config=plugger.resolve(Config),
        tool_runner=plugger.resolve(ToolRunner),
        context_manager=plugger.resolve(ContextManager),
        cancellation=plugger.resolve(Cancellation),
    )

    sys.exit(runaway.run(core.main()))
