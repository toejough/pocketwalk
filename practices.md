# Core vs Shell

Anything core to the logic/algorithm/features of the module goes in 'core'.

Everything else goes in 'shell.'

For every function/data-structure, if someone else could supply a different
implementation and that wouldn't change the core functionality/intent/features of your
app, then that function/data-structure goes in the shell.

# Async vs sync

Pure functions should be sync, impure functions should be async.

# Pure Async

Experimental.

Anything that only calls functions (no direct branching logic) is pure async.
All async functions should be pure async.

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
* core -> shell -> plugin|(adapter -> external) for everything.
* the core is what is essential to a thing's being/process/feature list.
  If the logic were handled by a plugin and implemented differently, and that would
  be a material difference to the purpose of the core, then the logic belongs in the
  core.  Otherwise, it belongs in an interactor, which is accessed via the shell.
* The shell is how the core interacts with all non-essential logic and side-effects.
  This way, the core does not care who implements the logic, or in what groupings, etc.
  This also enforces that the implementors provide the API the core wants to use, rather
  than forcing the core to use the API the implementors provide.
* The shell plug-ins can be adapters against 3rd party or generic libs, or purpose-built plugins.
* adapters should only wrap/adapt behavior of the libs, not define net-new behavior
* async/await for impure functions
* make functions pure by default, impure only if necessary
* multi-step async flows that should be 'atomic' need error handling/rollback logic.
* shell is a per-function plugin manager.  Plugins are passed into the shell, and the shell:
    * identifies unfulfilled functions
    * identifies matches in plugin
    * warns for matches that don't match annotations/signatures
    * warns for matches that are already fulfilled, unless those matches are composable/mappable
    * replaces unfulfilled shell functions
    * raises an exception if there are any unfulfilled functions
    * functions decorated with single-plugin, concurrent-plugin, get fulfilled

