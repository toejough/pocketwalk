#! /usr/bin/env python
# coding: utf-8


"""Pocketwalk."""


# [ Imports ]
# [ -Python ]
import pathlib
import select
import subprocess
import sys
import termios
# [ -Third Party ]
from runaway import signals


# [ API ]
def get_vcs():
    """Get the vcs plugin."""
    return VCS()


# [ Internal ]
class VCS:
    """VCS plugin for the pocketwalk shell."""

    def __init__(self):
        """Init the state."""
        self._vcs_future = None
        self._notified = False

    # [ API ]
    async def update_vcs(self, config, *, tool_state):
        """Handle version control actions."""
        if await self._exception_occurred():
            await self._re_raise_exception()
        elif await self._should_stop_vcs(config, tool_state=tool_state):
            await self._stop_vcs()
            self._notified = False
        elif await self._should_start_vcs(config, tool_state=tool_state):
            await self._start_vcs(config)
            self._notified = False
        elif await self._should_notify(config, tool_state=tool_state):
            print("No changes detected - no updates to commit.")
            self._notified = True

    def vcs_running(self):
        """Return whether or not vcs is running."""
        return bool(self._vcs_future)

    async def cleanup(self):
        """Clean up a running vcs future."""
        if self._vcs_future:
            print("Cleaning up VCS tasks...")
            await signals.cancel(self._vcs_future)
            self._vcs_future = None
            print("Done.")

    # [ Internal ]
    async def _should_notify(self, config, *, tool_state):
        """Return whether or not to notify."""
        return (
            not config['no_vcs'] and
            not self._vcs_future and
            not await self._any_tools_are_running(tool_state) and
            not await self._not_all_tools_passed(tool_state) and
            not self._notified
        )

    async def _any_tools_are_running(self, tool_state):
        """Return whether or not any tools are running."""
        return any(t['running'] for t in tool_state.values())

    async def _not_all_tools_passed(self, tool_state):
        """Return whether or not all the tools have passed."""
        return not all(t['return code'] == 0 for t in tool_state.values())

    async def _get_all_tracked_paths(self, config):
        """Get all tracked."""
        tools = config['tools']
        tracked = []
        for this_tool in tools:
            tracked += config[f'{this_tool}_targets']
            tracked += config[f'{this_tool}_triggers']
        tracked.append(config['config_path'])

        return list(set(tracked))

    async def _exception_occurred(self):
        """Return whether or not an exception occurred."""
        return self._vcs_future and self._vcs_future.exception

    async def _re_raise_exception(self):
        """Raise the exception."""
        raise self._vcs_future.exception[1].with_traceback(self._vcs_future.exception[2])

    async def _vcs_is_running(self):
        """Return whether vcs is running."""
        return self._vcs_future

    async def _stop_vcs(self):
        """Stop the vcs."""
        await signals.cancel(self._vcs_future)
        self._vcs_future = None

    async def _start_vcs(self, config):
        """Start the vcs."""
        self._vcs_future = await signals.future(self._run_vcs, config)

    async def _run_vcs(self, config):
        """Run the VCS commands."""
        to_remove = await self._get_missing_vcs_paths()
        to_add = await self._get_new_vcs_paths(config)
        changed = await self._get_changed_vcs_paths(config)
        await self._show_user_changes(
            to_remove=to_remove,
            to_add=to_add,
            changed=changed,
        )
        print('prompting for commit message...')
        commit_message = await self._prompt_for_commit_message()
        self._remove_missing_vcs_paths(to_remove)
        self._add_paths_to_vcs(to_add)
        self._add_paths_to_vcs(changed)
        self._commit_vcs(commit_message)
        self._vcs_future = None
        self._notified = True

    async def _get_missing_vcs_paths(self):
        """Get paths to remove."""
        status_lines = subprocess.run(
            ['git', 'status', '--porcelain'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        ).stdout.splitlines()
        to_delete = [l.strip().split(' ', 1)[-1] for l in status_lines if l.strip().startswith('D')]
        return to_delete

    async def _get_new_vcs_paths(self, config):
        """Get paths to add."""
        # XXX use path for all paths
        # XXX for git use git root instead of cwd
        status_lines = subprocess.run(
            ['git', 'status', '--porcelain'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        ).stdout.splitlines()
        to_add = [l.strip().split(' ', 1)[-1] for l in status_lines if l.startswith('??')]
        tracked = [
            str(pathlib.Path(p).absolute().relative_to(pathlib.Path.cwd()))
            for p in await self._get_all_tracked_paths(config)
        ]
        tracked_to_add = [l for l in to_add if l in tracked]
        directories = [l for l in to_add if l.endswith('/')]
        in_new_dir = [t for t in tracked if any(t.startswith(d) for d in directories)]
        return tracked_to_add + in_new_dir

    async def _get_changed_vcs_paths(self, config):
        """Get paths which changed."""
        status_lines = subprocess.run(
            ['git', 'status', '--porcelain'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        ).stdout.splitlines()
        to_add = [l.strip().split(' ', 1)[-1] for l in status_lines if l.strip().startswith('M')]
        tracked = [
            str(pathlib.Path(p).absolute().relative_to(pathlib.Path.cwd()))
            for p in await self._get_all_tracked_paths(config)
        ]
        tracked_to_add = [l for l in to_add if l in tracked]
        return tracked_to_add

    async def _show_user_changes(self, *, to_remove, to_add, changed):
        """Show the user changes."""
        print(f"removing: {to_remove}")
        print(f"adding: {to_add}")
        print(subprocess.run(
            ['git', 'diff', '--color', '--'] + changed,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        ).stdout.decode('utf-8'))

    async def _async_input(self, prompt: str) -> str:
        """Async input prompt."""
        readable = []  # type: List[int]
        print(prompt, end='')
        sys.stdout.flush()
        while not readable:
            readable, _writeable, _executable = select.select([sys.stdin], [], [], 0)
            try:
                await signals.sleep(0)
            except GeneratorExit:
                print("input cancelled...")
                termios.tcflush(sys.stdin, termios.TCIFLUSH)
                raise
        return sys.stdin.readline().rstrip()

    async def _prompt_for_commit_message(self):
        """Prompt for commit message."""
        print("your files are still being monitored for changes.")
        print("if changes are made, the commit will be cancelled and you will be reprompted when all the checks pass again.")
        return await self._async_input("commit message: ")

    @staticmethod
    def _remove_missing_vcs_paths(to_remove):
        """Remove missing vcs paths."""
        if to_remove:
            subprocess.run(['git', 'rm'] + to_remove)

    @staticmethod
    def _add_paths_to_vcs(to_add):
        """Add vcs paths."""
        if to_add:
            subprocess.run(['git', 'add'] + to_add)

    @staticmethod
    def _commit_vcs(message):
        """Commit changes to vcs."""
        subprocess.run(['git', 'commit', '-m', message])

    async def _paths_changed(self, config):
        """Return whether or not the paths changed."""
        return (
            await self._get_missing_vcs_paths() or
            await self._get_new_vcs_paths(config) or
            await self._get_changed_vcs_paths(config)
        )

    async def _should_stop_vcs(self, config, *, tool_state):
        """Return whether or not to stop vcs."""
        return await self._vcs_is_running() and (
            await self._any_tools_are_running(tool_state) or
            await self._not_all_tools_passed(tool_state) or
            not await self._paths_changed(config) or
            config['no_vcs']
        )

    async def _should_start_vcs(self, config, *, tool_state):
        """Return whether or not to start vcs."""
        return (
            not config['no_vcs'] and
            not await self._vcs_is_running() and
            not (
                await self._any_tools_are_running(tool_state) or
                await self._not_all_tools_passed(tool_state)
            ) and
            await self._paths_changed(config)
        )


# [ Vulture ]
assert all((
    get_vcs,
))
