# Core/Shell/Plugin

Anything core to the logic/algorithm/features of the module goes in 'core'.

Everything else goes into a plugin, which is defined in 'shell'.

For every function/class/data-structure, if someone else could supply a different
implementation and that wouldn't change the core functionality/intent/features of your
app, then that function/data-structure's description goes in the shell, and implementations come from plugins.

# Async vs sync

Pure functions should be sync, impure functions should be async.

Treat everything coming in from a plugin as async, unless you
specifically want to indicate that that thing should be sync, and
are willing to pay penalties if the implementor decides it can be better done with some async code.

If you treat everything from the shell as async, you leave it up to the implementation whether to use sync/async under the covers.

# Pure Async

Anything async that only calls functions (no direct branching logic) is pure async.

As with pure functions, prefer pure async functions.

# Test vs no test

Anything that is a pure function needs unit tests.
These functions need to be tested with a variety of inputs and outputs.

Anything that is a pure async function is meaningless to test.  You are
unable to guarantee actual runtime inputs/outputs mid-function, so the
best you can do is test that the right functions get called mid-func given
the responses from the initial call or previous mid-func functions.  Effectively,
you are writing a shadow copy of the test function, implementation-detail-for-implementation-detail.

This is counterproductive and provides no real benefit.

Mixed-mode functions do need to be tested - there are now different input/output chains.

# Intent

Every function should express a single intent.  This is especially important for pure async functions,
whose only real testing is going to be code review and E2E runtime behavior.

Development Notes:
* core -> shell -> plugin for everything.
* the core is what is essential to a thing's being/process/feature list.
  If the logic were handled by a plugin and implemented differently, and that would
  be a material difference to the purpose of the core, then the logic belongs in the
  core.  Otherwise, it belongs in a plugin, which is accessed via the shell.
* The shell is how the core interacts with all non-essential logic and side-effects.
  This way, the core does not care who implements the logic, or in what groupings, etc.
  This also enforces that the implementors provide the API the core wants to use, rather
  than forcing the core to use the API the implementors provide.
* The shell plug-ins can be adapters against 3rd party or generic libs, or purpose-built plugins.
* async/await for impure functions
* make functions pure by default, impure only if necessary
* make async functions pure async by default, impure only if necessary
* multi-step async flows that should be 'atomic' need error handling/rollback logic.
* plugins are:
    * discovered by namespace
    * self-filtered (pass in arbitrary object for use in self-filtering)
    * caller-filtered (request an arbitrary object for use in caller filtering)
    * error if non-multi plugin-target has multiple matching plugins after filtering
    * error if no matching plugins after filtering
    * returned to the caller for use wherever necessary (generally, passed into the core)
    * checked for various guarantees - either the default or passed in validation
* spec -> tests -> code -> vulture -> pylint -> flake8 -> arch-review -> mypy -> API-checklist -> documentation-checklist
* details should go into properties/context-managers/decorators
