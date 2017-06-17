# pocketwalk

Watch, run, commit.

# What it does (short version)

* watches your code for changes
* runs static checkers against it
* commits when all checks pass

The commit tool at the moment is git-only.  If there's enough demand, it can be updated to allow other VCS tools.

# What it does (long version)

* reads the config and CLI for how to run
    * config path defaults to `./.pocketwalk.toml`
    * the CLI takes precedence over the config
* runs the given tools with the given paths
* each tool is run to completion
* if all tools pass, you are shown the changes since the last commit, and prompted to commit them (unless you've disabled vcs)
* if any tool fails, pocketwalk waits for you to fix it (unless you're just running once)
* after commit, the tool continues to watch your files & repeats (unless you're running just till passing)

Changes to files will stop and restart affected tools mid run, including the VCS commit action.

# Example use

`.pocketwalk.toml`:

    ```toml
    run = "forever"

    [tools.pylint]
    config = "{affected_targets}"
    target_paths = "**/*.py"
    trigger_paths = ".pylintrc"
    preconditions = []

    [tools.vulture]
    config = "."
    trigger_paths = "**/*.py"

    [tools.dodgy]
    trigger_paths = "**/*.py"

    [tools.flake8]
    config = "{affected_targets}"
    target_paths = "**/*.py"
    trigger_paths = ".flake8"

    [tools.pytest]
    config = "{affected_targets}"
    target_paths = "**/test*.py"
    trigger_paths = "**/*.py"
    preconditions = ['pylint', 'vulture', 'flake8', 'dodgy']
    ```

At your shell, run:

    `pocketwalk`

This will run pylint, vulture, dodgy, and flake8 tools.  They will run in parallel, and output their results, *then* run pytest, *then* prompt you for a commit if you have uncommited file changes.

If running in the default continuous mode, you stop it with `ctrl-c`.

# Installation

`pip install pocketwalk`

# Naming
"(watch|check)[er|it]" and other variations have been taken, so I thought I'd make a play on the words "Watch" (pocketwatch) and "Run" (walk).
