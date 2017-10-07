"""
Pocketwalk.

Basics:
* load config
* run tools
* run vcs
* exit app

Extras:
* Use a tool controller that stops/starts tools on config change
* tool controller stops/starts tools on relevant file changes
* tools only run targets that have (failed or changed since last success) with current
  tool config and trigger file states
* vcs controller stops/starts VCS on file changes
* Exit handler gracefully exits on ctrl-c
* loop option to loop forever
* loop option to loop till passing
* vcs option to skip vcs
"""


# [ Imports ]
# [ -Python ]
import types
# [ -Third Party ]
import sagas


# [ Core ]
@sagas.saga(types.SimpleNamespace())
def _main() -> None:
    """Main function."""
    return (
        load_config,
        run_tools,
        run_vcs,
        exit_app,
    )


# [ Main ]
sagas.run_saga(_main)
