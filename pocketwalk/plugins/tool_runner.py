#! /usr/bin/env python
# coding: utf-8


"""Pocketwalk tool runner."""


# [ Imports ]
# [ -Python ]
import os
import pathlib
import pty
import selectors
import subprocess
import sys
from pprint import pprint
# [ -Third Party ]
import pytoml as toml
from runaway import signals


# [ API ]
def get_tool_runner():
    """Get the tool runner plugin."""
    return ToolRunner()


# [ Internal ]
class ToolRunner:
    """Tool Runner Plugin."""

    def __init__(self):
        """Init the state."""
        self._running_tools = {}
        self._return_codes = {}
        self._reported_tools = {}

    # [ API ]
    async def get_tool_state(self):
        """Get the tool state."""
        state = {}
        for tool, return_code in self._return_codes.items():
            state[tool] = {
                'running': False,
                'return code': return_code,
            }
        for tool in self._running_tools:
            state[tool] = {
                'running': True,
                'return code': None,
            }
        return state

    def all_tools_passed(self, tools):
        """Return whether all of the tools have passed."""
        return all(self._return_codes.get(t, None) == 0 for t in tools)

    def any_tools_not_done(self):
        """Return whether any of the tools are not done."""
        return bool(self._running_tools)

    async def return_codes(self, tools):
        """Return the return codes."""
        return [self._return_codes[t] for t in tools if t in self._return_codes]

    async def ensure_tools_running(self, contexts_for_tools, *, on_completion):
        """
        Ensure the tools are running with their current contexts.

        Calls the on_completion function with the tool and RC on completion of each tool.
        Runs the tools concurrently.
        """
        tools = contexts_for_tools.keys()

        tools_to_start = [t for t in tools if t not in self._running_tools]

        if tools_to_start:
            print(f"Starting tools: {tools_to_start}")

        for this_tool in tools_to_start:
            if this_tool in self._return_codes:
                del self._return_codes[this_tool]
            self._running_tools[this_tool] = {
                'context': contexts_for_tools[this_tool],
                'process future': await signals.future(
                    self._run_tool,
                    this_tool,
                    context=contexts_for_tools[this_tool],
                    on_completion=on_completion,
                ),
            }

        for state in self._running_tools.values():
            exc_info = state['process future'].exception
            if exc_info:
                raise exc_info[1].with_traceback(exc_info[2])

    async def get_tools_failing_preconditions(self, contexts, *, tools_to_run):
        """Get the tools which are failing their preconditions."""
        failing = {}
        for tool, current_context in contexts['current_state'].items():
            if not all(self._return_codes.get(t, None) == 0 for t in current_context['preconditions']):
                failing[tool] = current_context
            if any(t in current_context['preconditions'] for t in tools_to_run):
                failing[tool] = current_context
        return failing

    async def filter_out_reported_tools(self, tools_with_contexts):
        """Filter out any previously reported tools."""
        unreported_tools = {}
        for tool, context in tools_with_contexts.items():
            reported_context = self._reported_tools.get(tool, None)
            context = context.copy()
            if 'affected files' in context:
                del context['affected files']
            if reported_context != context:
                unreported_tools[tool] = context
        return unreported_tools

    async def cleanup(self):
        """Ensure the tools are stopped."""
        print("Cleaning up tools...")
        tools_to_stop = list(self._running_tools.keys())

        for this_tool in tools_to_stop:
            await signals.cancel(self._running_tools[this_tool]['process future'])
            del self._running_tools[this_tool]
            self._return_codes[this_tool] = 130

        if tools_to_stop:
            print(f"Cancelled running tools: {tools_to_stop}")

        print("Done.")

    async def ensure_stale_tools_stopped(self, contexts_for_tools):
        """
        Ensure the tools are stopped.

        Stops the given tools if their contexts are stale.
        """
        tools = contexts_for_tools.keys()

        tools_to_stop = [t for t in tools if t in self._running_tools and (
            self._running_tools[t]['context'] != contexts_for_tools[t]
        )]

        for this_tool in tools_to_stop:
            await signals.cancel(self._running_tools[this_tool]['process future'])
            del self._running_tools[this_tool]

        if tools_to_stop:
            print(f"Stopped stale tools: {tools_to_stop}")

    async def ensure_tools_stopped(self, contexts_for_tools, *, reason):
        """Ensure the tools are stopped."""
        tools_to_stop = [t for t in self._running_tools if t in contexts_for_tools]

        for this_tool in tools_to_stop:
            await signals.cancel(self._running_tools[this_tool]['process future'])
            del self._running_tools[this_tool]

        if tools_to_stop:
            print(f"Stopped tools with {reason}: {tools_to_stop}")

    async def ensure_removed_tools_stopped(self, config):
        """Ensure tools not in the tools list are stopped."""
        tools_to_stop = [t for t in self._running_tools if t not in config['tools']]

        for this_tool in tools_to_stop:
            await signals.cancel(self._running_tools[this_tool]['process future'])
            del self._running_tools[this_tool]

        if tools_to_stop:
            print(f"Stopped removed tools: {tools_to_stop}")

    async def replay_previous_results_for(self, tools):
        """Replay the previous results for the given tools."""
        previous_results = {t: {
            'output': (
                pathlib.Path.cwd() / '.pocketwalk.cache' / t
            ).with_suffix('.output').read_bytes(),
            'return code': max(toml.loads((
                pathlib.Path.cwd() / '.pocketwalk.cache' / t
            ).with_suffix('.return_codes').read_text()).values()),
        } for t in tools.keys()}
        return_codes = []
        for this_tool, results in previous_results.items():
            print(f"{this_tool} is unchanged.  Last output:")
            print(results['output'].decode('utf-8'))
            self._report_tool_result(this_tool, return_code=results['return code'])
            return_codes.append(results['return code'])
            self._return_codes[this_tool] = results['return code']
        for this_tool, context in tools.items():
            context = context.copy()
            if 'affected files' in context:
                del context['affected files']
            self._reported_tools[this_tool] = context
        return return_codes

    # [ Internal ]
    @staticmethod
    def _report_tool_result(tool, *, return_code):
        """Report the tool's result."""
        if return_code != 0:
            print(f"{tool} failed with RC {return_code}")
        else:
            print(f"{tool} passed")

    @staticmethod
    def _process_output(stdout):
        """Process the output."""
        line = os.read(stdout, 1024)
        if line:
            sys.stdout.buffer.write(line)
            sys.stdout.flush()

        return line

    async def _run_tool(self, tool, *, context, on_completion):
        """Run a single tool."""
        if tool in self._return_codes:
            del self._return_codes[tool]
        previous_rcs = await self._load_rcs(tool, context=context)
        targets_used = self._get_targets(previous_rcs=previous_rcs, context=context)
        substituted = []
        # add previously failing targets that are still valid targets to the list to run
        for this_arg in context['config']:
            if this_arg == '{affected_targets}':
                substituted += targets_used
            else:
                substituted.append(this_arg)
        args = [tool] + substituted
        if not targets_used:
            targets_used = ["*"]
        pprint(args)
        output, process = await self._run_pty(args)

        self._report_tool_result(tool, return_code=process.returncode)
        await on_completion(tool, context=context)
        (pathlib.Path.cwd() / '.pocketwalk.cache' / tool).with_suffix('.output').write_bytes(output)
        await self._save_rcs(tool, targets_used=targets_used, return_code=process.returncode, previous_rcs=previous_rcs)
        self._return_codes[tool] = process.returncode
        context = context.copy()
        if 'affected files' in context:
            del context['affected files']
        self._reported_tools[tool] = context
        del self._running_tools[tool]
        if not self._running_tools:
            print("No tools running.")

    async def _load_rcs(self, tool, *, context):
        """Load saved RC's."""
        rc_path = (pathlib.Path.cwd() / '.pocketwalk.cache' / tool).with_suffix('.return_codes')
        # TOML parsing
        try:
            previous_rcs = {path: rc for path, rc in toml.loads(rc_path.read_text()).items() if path in context['target files']}
        except FileNotFoundError:
            previous_rcs = {}
        return previous_rcs

    async def _save_rcs(self, tool, *, targets_used, return_code, previous_rcs):
        """Save RC's."""
        rc_path = (pathlib.Path.cwd() / '.pocketwalk.cache' / tool).with_suffix('.return_codes')
        # save old RC's for current targets
        new_rcs = {}
        for path in list(previous_rcs.keys()):
            new_rcs[path] = previous_rcs[path]
        # save the actual RC's for paths that were used
        for path in targets_used:
            new_rcs[path] = return_code
        rc_path.write_text(toml.dumps(new_rcs))

    @staticmethod
    def _get_targets(*, context, previous_rcs):
        """Get targets for the tool."""
        targets_used = []
        # add previously failing targets that are still valid targets to the list to run
        for path, return_code in list(previous_rcs.items()):
            if return_code != 0:
                targets_used.append(path)
        if '{affected_targets}' in context['config']:
            targets_used += context['affected files']
        return list(set(targets_used))

    async def _run_pty(self, args):
        """Run a PTY."""
        try:
            # make a pseudo terminal for the subprocess so we get colors and such
            output_side, input_side = pty.openpty()
            process = subprocess.Popen(args, stdout=input_side, stderr=subprocess.STDOUT, start_new_session=True)
            await signals.sleep(1)

            selector = selectors.DefaultSelector()
            selector.register(output_side, selectors.EVENT_READ, self._process_output)

            output = b''
            while selector.get_map():
                await signals.sleep(0)
                events = selector.select(0)
                for key, _mask in events:
                    output += key.data(output_side)
                if process.poll() is not None:
                    break

            while process.poll() is None:
                signals.sleep(0)

            return output, process

        except GeneratorExit:
            print("TERMINATED")
            process.terminate()
            process.kill()
            raise

        finally:
            os.close(input_side)
            os.close(output_side)
            selector.close()


# [ Vulture ]
assert all((
    get_tool_runner,
))
