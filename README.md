# static-checker
A python async static checker.  Dev status: Alpha

Built with python async features.

Built for python static checking, but should work with any tool which accepts a list of file paths at the end of its CLI args, and the files don't have to be python.

# What it does (short version)

* watches your code for changes
* runs static checkers against it
* commits when all checks pass

# What it does (long version)

* reads the CLI args for a config path and how to run
  * config path defaults to `./check.yaml`
  * how to run defaults to continuous - you can override and tell it to run once
* reads the config file for files to watch (will always also watch the config file for changes!)
* reads the config file for checks to run (will always pass all specified file paths to checker as CLI args (but not the config file))
* runs checks on all files once
* unless overridden on the CLI, watches the specified files (and the config) and on any change:
  * cancels any running check or commit
  * re-reads the config file
  * re-runs the checks (in parallel!)

On any check failure, any other still-running checks are cancelled.

On all checks pass, the repo diff is displayed, and you are prompted for a commit message.
* if you enter a message, the diffs are committed and you are dropped back to a waiting message while the tool waits for more changes.
* else, the prompt sits there waiting, but the files are still being scanned in the meantime.  Any changes made while the prompt is up will cancel the commit and restart the checks.

## Fun features
### Config file reload
As mentioned several times, the config file is re-loaded on every modification.  This means:
* changes to the file list actually change the checked files - no need to restart the watcher
* changes to the checker list actually change the checks run - no need to restart the watcher

### Git auto-add
Any new files added to the config to check, which are not checked into git, will be added to git when a commit is made.

### Fast-fail
This has already been mentioned elsewhere, but the tool fails fast.  The checks are run in parallel, and the first check to fail cancels any still-running checks.  The workflow is change-check-fix-repeat.  The tool is opinionated in that it expects that you want to fix any and all failures ASAP, so it stops and reports to you as soon as a failure is discovered.

### Always-fresh results
The tool continues to watch the files for changes, even while running checkers or waiting for your commit message.  Any time a change is detected, running checks or commits are aborted and the checks are run again.  This ensures that you're always only seeing the failures in the current code on disk, and (perhaps more importantly), only committing code that has actually passed all of your checks.

### Git diff
Successful checks result in a git diff of the current code against the last commit being shown.

### Git commit
Successful checks result in a prompt for a commit message, which is used to commit your changes.  Commits are only made if you provide a message - if you don't want to commit a small change, don't.  The tool continues to watch for changes and will cancel the commit and restart the checking/commit process whenever a new modification is discovered.


# Installation
`git clone https://github.com/toejough/static-checker.git`

install python 3 if you don't have it yet:
`brew install python3`

pip install all the third-party libs:

* `a_sync` - python async helpers
* `blessed` - python terminal-fu
* `pyaml` - python YAML lib

Add the installation dir to your path:
`export PATH=$PATH:<path-to-static-checker-repo>`

# Running
`static-checker`

That'll error out telling you you need a config file.

example config file:
```yaml
paths:
    - alexa/__init__.py

checks:
    - [vulture]
    - [prospector]
    - [mypy, -s, --fast-parser, --disallow-untyped-defs]
```

Add a config file (named `check.yaml` by default, you can name it anything and pass it as a cli arg).

Run again: `static-checker`.

If running in the default continuous mode, you stop it with `ctrl-c`.
