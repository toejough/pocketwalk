# coding: utf-8


"""Test pocketwalk."""


# [ Imports ]
# [ -Python
# import typing
# # [ -Third Party ]
# import dado
# from runaway import extras, signals, testing
# import utaw
# # [ -Project ]
# import pocketwalk
# from pocketwalk.core import checkers, commit


# [ Expectations ]
# checkers are configured in per checker config files
# each checker has:
#   an optional name
#   an optional config file,
#   a checker path
#   a path watch list,
#   an arg string
# templated args:
#   config: the checker's config file (but not the pocketwalk config for that checker)
#   passed: paths which passed the last run
#   failed: paths which failed the last run
#   changed: paths which changed since the last run
#   new: paths which haven't been run
#   removed: paths which have been removed since the last run
#   all: passed | failed | changed | new

# paths used are stored in a records file
# each path has:
#   the path
#   the checkers that care about it
#   whether the last run using that file since addition/change: passed/failed/didn't-complete, per checker

# single run:
# if there are paths & they all pass all checkers & commit passes (if commit was necessary), then we pass
# if there are no paths, the tool exits with that result (no paths)
# if there are paths, but they don't pass all checkers, or the commit is necessary but doesn't pass, we wait.
# if a stop is sent via input queue, a "stopped" result is returned
# watchers for all are running during all checks/commits
# when a file changes, checks for that file are restarted, and active commits are cancelled
# when we return, all watchers are cancelled
# commit is triggered when all paths pass & any paths are (not ignored & (changed|new|removed))
# commits commit changes, new files, removed files
# procedural actions and results are reported back to the caller via a timestamped queue
# subprocess output is reported back to the caller via the same queue, line by line
# loops until an exit condition

# continuous run:
# same, but we never return pass or no-tool, just wait for the next change.


# [ Static Checking ]
# this is a test module - we're doing protected accesses.
# pylint: disable=protected-access


# [ Test Objects ]
class App:
    """Application test object."""



# [ Tests ]
def test_single_checker_single_run_no_changes() -> None:
    """Test running a single checker to success once, on the first try, with no changes."""
    app = App()
    app.reports_startup()
    app.reports_loading_config()
    app.reads_config_and_receives({
        "checkers": {
            "foo": {
                "config": ".foo.config",
                "paths": ["**/*.py"],
                "args": "--added {added} --removed {removed} --changed {changed} --all {all} --other-args abcd efgh",
            }
        }
    })
    app.reports_config()
    app.reports_loading_records()
    app.reads_record_and_receives({"checkers": {"foo": {"bar.py": "abcdef", "baz.py": "012345"}}})
    app.reports_records()
    app.reports_scanning_paths()
    app.scans_paths_and_receives({"bar.py": "abcdef", "baz.py": "012345"})
    app.calculates_path_differences_and_determines([])
    app.reports_path_results()
    app.returns(pocketwalk.Results.SUCCESS)


# [ Test Objects ]
# class Loop:
#     """Loop test steps."""

#     def __init__(self) -> None:
#         """Init state."""
#         self._coro = testing.TestWrapper(pocketwalk.loop())

#     def loops_single(self) -> None:
#         """Verify the loop call and return."""
#         testing.assertEqual(
#             self._coro.signal,
#             signals.Call(
#                 extras.run_forever,
#                 pocketwalk.run_single,
#                 None,
#             ),
#         )
#         self._coro.receives_value(None)

#     def returns(self) -> None:
#         """Verify the exit call and return."""
#         utaw.assertIsNone(self._coro.returned)


# class RunSingle:
#     """Run the test steps a single time."""

#     def __init__(self) -> None:
#         """Init state."""
#         self._coro = testing.TestWrapper(pocketwalk.run_single())

#     def runs_checkers_until_all_pass(self) -> None:
#         """Verify coro runs checkers and mock the given result."""
#         testing.assertEqual(self._coro.signal, signals.Call(checkers.run_until_all_pass))
#         self._coro.receives_value(None)

#     def runs_commit_and_gets(self, result: commit.Result) -> None:
#         """Verify coro runs commit and mock the given result."""
#         testing.assertEqual(self._coro.signal, signals.Call(commit.run))
#         self._coro.receives_value(result)

#     def returns(self, status: commit.Result) -> None:
#         """Verify coro returns the given status."""
#         utaw.assertIs(self._coro.returned, status)


# class CheckerLoop:
#     """Checker loop test steps."""

#     def __init__(self) -> None:
#         """Init state."""
#         self._coro = testing.TestWrapper(checkers.run_until_all_pass())

#     def loops_single(self) -> None:
#         """Verify the loop call and return."""
#         testing.assertEqual(
#             self._coro.signal,
#             signals.Call(
#                 extras.do_while,
#                 checkers._not_all_passing,
#                 checkers._run_single,
#                 None,
#             ),
#         )
#         self._coro.receives_value(None)

#     def returns(self) -> None:
#         """Verify the exit call and return."""
#         utaw.assertIsNone(self._coro.returned)


# class CheckerRunSingle:
#     """Run the checker steps a single time."""

#     def __init__(self) -> None:
#         """Init state."""
#         self._coro = testing.TestWrapper(checkers._run_single(None))

#     def gets_checker_list_and_receives_list(self) -> None:
#         """Verify coro runs checkers and mock the given result."""
#         testing.assertEqual(self._coro.signal, signals.Call(checkers._get_checker_list))
#         self._coro.receives_value(None)

#     def cancels_removed_checkers(self) -> None:
#         """Verify coro cancels removed checkers and mock the given result."""
#         testing.assertEqual(self._coro.signal, signals.Call(checkers._cancel_removed_checkers))
#         self._coro.receives_value(None)

#     def launches_new_checkers(self) -> None:
#         """Verify coro launches new checkers and mock the given result."""
#         testing.assertEqual(self._coro.signal, signals.Call(checkers._launch_new_checkers))
#         self._coro.receives_value(None)

#     def relaunches_changed_checkers(self) -> None:
#         """Verify coro relaunches changed checkers and mock the given result."""
#         testing.assertEqual(self._coro.signal, signals.Call(checkers._relaunch_changed_checkers))
#         self._coro.receives_value(None)

#     def launches_watchers_for_completed_checkers(self) -> None:
#         """Verify coro launches watchers for completed checkers and mock the given result."""
#         testing.assertEqual(self._coro.signal, signals.Call(checkers._launch_watchers_for_completed_checkers))
#         self._coro.receives_value(None)

#     def launches_watcher_for_checker_list(self) -> None:
#         """Verify coro launches watcher for checker list and mock the given result."""
#         testing.assertEqual(self._coro.signal, signals.Call(checkers._launch_watcher_for_checker_list))
#         self._coro.receives_value(None)

#     def waits_for_any_future(self) -> None:
#         """Verify coro waits for any future and mock the given result."""
#         testing.assertEqual(self._coro.signal, signals.Call(checkers._wait_for_any_future))
#         self._coro.receives_value(None)

#     def analyzes_checker_state_and_gets(self, status: checkers.Result) -> None:
#         """Verify coro waits for any future and mock the given result."""
#         testing.assertEqual(self._coro.signal, signals.Call(checkers._analyze_checker_state))
#         self._coro.receives_value(status)

#     def cancels_all_futures(self) -> None:
#         """Verify coro cancels all futures and mock the given result."""
#         testing.assertEqual(self._coro.signal, signals.Call(checkers._cancel_all_futures))
#         self._coro.receives_value(None)

#     def returns(self, status: checkers.Result) -> None:
#         """Verify coro returns given status."""
#         testing.assertEqual(self._coro.returned, status)


# class CheckerRunSinglePredicate:
#     """Checker loop predicate test steps."""

#     def __init__(self, status: checkers.Result) -> None:
#         """Init state."""
#         async def wrapped(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
#             """Run function as coro."""
#             return checkers._not_all_passing(*args, **kwargs)

#         self._coro = testing.TestWrapper(wrapped(status))

#     def returns(self, result: bool) -> None:
#         """Verify the exit call and return."""
#         utaw.assertIs(self._coro.returned, result)


# class CheckerRemoverLoop:
#     """Checker remover loop test steps."""

#     def __init__(self, checkers_to_cancel: list) -> None:
#         """Init state."""
#         self._checkers_to_cancel = checkers_to_cancel
#         self._coro = testing.TestWrapper(checkers._cancel_removed_checkers(self._checkers_to_cancel))

#     def loops_single(self) -> None:
#         """Verify the loop call and return."""
#         testing.assertEqual(
#             self._coro.signal,
#             signals.Call(
#                 extras.do_while,
#                 checkers._checkers_to_cancel,
#                 checkers._cancel_single,
#                 self._checkers_to_cancel,
#             ),
#         )
#         self._coro.receives_value(None)

#     def returns(self) -> None:
#         """Verify the exit call and return."""
#         utaw.assertIsNone(self._coro.returned)



# # [ Loop Tests ]
# def test_loop() -> None:
#     """
#     Test the main loop.

#     When called, the main loop should run, and when the passed in predicate evaluates to False,
#     return None.
#     """
#     the_loop = Loop()
#     the_loop.loops_single()
#     the_loop.cancels_running_watchers()
#     the_loop.returns()


# def test_run_single_happy_path() -> None:
#     """Test the run_single happy path."""
#     run_single = RunSingle()
#     run_single.runs_checkers_until_all_pass()
#     run_single.runs_commit_and_gets(commit.Result.COMMITTED)
#     run_single.returns(commit.Result.COMMITTED)


# def test_run_single_change_during_commit() -> None:
#     """Test the run_single path when there is a change during a commit."""
#     run_single = RunSingle()
#     run_single.runs_checkers_until_all_pass()
#     run_single.runs_commit_and_gets(commit.Result.CHANGES_DETECTED)
#     run_single.returns(commit.Result.CHANGES_DETECTED)


# def test_run_single_commit_failure() -> None:
#     """Test the run_single path when there is failure during commit."""
#     run_single = RunSingle()
#     run_single.runs_checkers_until_all_pass()
#     run_single.runs_commit_and_gets(commit.Result.FAILED)
#     run_single.returns(commit.Result.FAILED)


# # [ Checker Loop ]
# def test_checker_loop() -> None:
#     """Test the run_checkers happy path."""
#     checker_loop = CheckerLoop()
#     checker_loop.loops_single()
#     checker_loop.returns()


# # [ Checker Single Run ]
# def test_checker_run_single_running() -> None:
#     """Test the single run for the checkers while checkers are running."""
#     run_single = CheckerRunSingle()
#     run_single.gets_checker_list_and_receives_list()
#     run_single.cancels_removed_checkers()
#     run_single.launches_new_checkers()
#     run_single.relaunches_changed_checkers()
#     run_single.launches_watchers_for_completed_checkers()
#     run_single.launches_watcher_for_checker_list()
#     run_single.waits_for_any_future()
#     run_single.analyzes_checker_state_and_gets(checkers.Result.RUNNING)
#     run_single.returns(checkers.Result.RUNNING)


# def test_checker_run_single_all_passing() -> None:
#     """Test the single run for the checkers while checkers are running."""
#     run_single = CheckerRunSingle()
#     run_single.gets_checker_list_and_receives_list()
#     run_single.cancels_removed_checkers()
#     run_single.launches_new_checkers()
#     run_single.relaunches_changed_checkers()
#     run_single.launches_watchers_for_completed_checkers()
#     run_single.launches_watcher_for_checker_list()
#     run_single.waits_for_any_future()
#     run_single.analyzes_checker_state_and_gets(checkers.Result.ALL_PASSING)
#     run_single.cancels_all_futures()
#     run_single.returns(checkers.Result.ALL_PASSING)


# # [ Checker Predicate ]
# @dado.data_driven(['status', 'result'], {
#     'all_passing': [checkers.Result.ALL_PASSING, False],
#     'running': [checkers.Result.RUNNING, True],
# })
# def test_checker_run_single_predicate(status: checkers.Result, result: bool) -> None:
#     """Test the single run predicate."""
#     predicate = CheckerRunSinglePredicate(status)
#     predicate.returns(result)


# # [ Cancel Removed Checkers ]
# def test_remove_checker_loop_no_checkers() -> None:
#     """Test the remove checker loop when there are no checkers to remove."""
#     checker_remover_loop = CheckerRemoverLoop([])
#     checker_remover_loop.returns()


# def test_remove_checker_loop_checkers() -> None:
#     """Test the remove checker loop when there are no checkers to remove."""
#     checker_remover_loop = CheckerRemoverLoop(['a', 'b', 'c'])
#     checker_remover_loop.loops_single()
#     checker_remover_loop.returns()
#     # get removed checkers
#     # if no removed checkers, return
#     # loop remove_single
#     # predicate -> any left
