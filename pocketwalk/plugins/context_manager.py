#! /usr/bin/env python
# coding: utf-8


"""Pocketwalk context manager."""


# [ Imports ]
# [ -Python ]
import hashlib
import pathlib
import time
# [ -Third Party ]
from runaway import signals
import pytoml as toml


# [ API ]
def get_context_manager():
    """Get the context_manager plugin."""
    return ContextManager()


# [ Internal ]
class ContextManager:
    """Context manager plugin for pocketwalk."""

    # [ API ]
    def get_tools_unchanged_since_last_results(self, contexts):
        """Get the tools whose contexts are unchanged since the last results."""
        return {tool: value['context'] for tool, value in self._tagged_contexts(contexts).items() if not value['changed']}

    def get_tools_changed_since_last_save(self, contexts):
        """Get the tools whose contexts have changed since the last save."""
        return {tool: value['context'] for tool, value in self._tagged_contexts(contexts).items() if value['changed']}

    async def get_tool_context_data(self, config):
        """Get tool context data."""
        last_context_per_tool_map = await signals.call(self._get_last_contexts_for, config)
        current_context_per_tool_map = await signals.call(self._get_contexts_for, config=config)
        return {
            'last_saved': last_context_per_tool_map,
            'current_state': current_context_per_tool_map,
        }

    @staticmethod
    def contexts_in_a_and_not_b(*, a_context, b_context):
        """Return the contexts in a and not in b."""
        to_return = {}
        for tool, context in a_context.items():
            if tool not in b_context:
                to_return[tool] = context
        return to_return

    @staticmethod
    async def save_context(tool, *, context):
        """Save the current context for the given tool."""
        context = context.copy()
        if 'affected files' in context:
            del context['affected files']
        pathlib.Path(pathlib.Path.cwd() / '.pocketwalk.cache').mkdir(parents=True, exist_ok=True)
        (pathlib.Path.cwd() / '.pocketwalk.cache' / tool).with_suffix('.context').write_text(toml.dumps(context))

    # [ Internal ]
    @staticmethod
    def _tagged_contexts(contexts):
        """Reduce the contexts to the latest, and tag them as changed/unchanged since the last save."""
        tagged_contexts = {}
        for tool, current_context in contexts['current_state'].items():
            last_context = contexts['last_saved'].get(tool, None)
            this_tagged_context = current_context.copy()
            changed = last_context != current_context
            this_tagged_context['affected files'] = []
            if (
                    last_context and
                    changed and
                    last_context['trigger files'] == this_tagged_context['trigger files'] and
                    last_context['config'] == this_tagged_context['config'] and
                    last_context['preconditions'] == this_tagged_context['preconditions']
            ):
                for file_name, file_hash in list(this_tagged_context['target files'].items()):
                    if last_context['target files'].get(file_name, None) != file_hash:
                        this_tagged_context['affected files'].append(file_name)
            else:
                this_tagged_context['affected files'] = this_tagged_context['target files']

            tagged = {'context': this_tagged_context, 'changed': changed}
            tagged_contexts[tool] = tagged
        return tagged_contexts

    def _get_contexts_for(self, config):
        """Get the current contexts for the given tools."""
        contexts = {}
        for this_tool in config['tools']:
            target_files = config[f'{this_tool}_targets']
            trigger_files = config[f'{this_tool}_triggers']
            args = config[f'{this_tool}_args']
            hashed_target_files = self._get_hashes_for(target_files)
            hashed_trigger_files = self._get_hashes_for(trigger_files)
            contexts[this_tool] = {
                'target files': hashed_target_files,
                'trigger files': hashed_trigger_files,
                'config': args,
                'preconditions': config[f'{this_tool}_preconditions'],
            }
        return contexts

    @staticmethod
    def _get_last_contexts_for(config):
        """Get the last contexts for the given tools."""
        tools = [t for t in config['tools'] if (pathlib.Path.cwd() / '.pocketwalk.cache' / t).with_suffix('.context').exists()]
        loaded_contexts = {t: toml.loads(
            (pathlib.Path.cwd() / '.pocketwalk.cache' / t).with_suffix('.context').read_text(),
        ) for t in tools}
        for context in loaded_contexts.values():
            context['config'] = context.get('config', [])
            context['preconditions'] = context.get('preconditions', [])
            context['trigger files'] = context.get('trigger files', {})
            context['target files'] = context.get('target files', {})
        return loaded_contexts

    @staticmethod
    def _get_hashes_for(path_strings):
        """Return sha hashes for the path strings."""
        tries = 0
        max_tries = 3
        while True:
            try:
                return {s: hashlib.sha1(pathlib.Path(s).read_bytes()).hexdigest() for s in path_strings}
            except FileNotFoundError:
                # Can happen if file is being written while we try to read
                if tries < max_tries:
                    time.sleep(0.1)
                    tries += 1
                    continue
                raise


# [ Vulture ]
assert all((
    get_context_manager,
))
