# The actors in the system


## Main

Primary job: main control

Created with: ()

Initial actions:
* creates UI actor
* registers with UI actor
* issues start message to UI
* creates path state actor, registers 

Messages Accepted:
* config to run (tool configs): issues cancel tool to each tool running which is missing, restart tool to each with a different config, issues tool to run to self to for each tool not running, asks UI for config
* cancel tool (tool): kills runner, issues status update to UI
* restart tool (tool): kills runner, issues status update to UI, issues tool to run message to self
* tool to run (tool, args, trigger paths): asks for states from path state actor
* path states (paths, states): creates system runner, issues registration message, issues start message, issues poll message, creates trigger watcher, registers, starts
* tool running (runner id): issues poll message
* tool result (runner id, result): issues kill to trigger watchers, issues result message to UI, issues kill message to system runner, issues kill message to UI, exits
* trigger changed (runner id): issues status update to UI, kills runner, issues tool to run message to self


## UI

Primary job: Interface with the user.

Created with: ()

Initial actions: None

Messages Accepted:
* register: registers caller for messages
* unregister: unregisters caller for messages
* start: gets initial input from user, parses, and issues command message
* result: prints result to screen
* status: prints status to screen
* kill: (closes inbox, kills owned actors, releases resources)


## System Runner

Primary job: run a system command

Created with: (command, args)

Initial actions: None

Messages accepted:
* start: start running the system command if not already running
* restart: stop running the system command if running, and restart
* poll: issues tool running to poller, or tool result to all registered


## Trigger watcher

Primary job: watch trigger paths

Created with: (paths, path states, path state actor)

Initial actions: None

Messages Accepted:
* start: asks path state actor for path states
* path states (paths, states): if matching, ask for path states, else, issue trigger changed and ask for path states


# Actors in general

* have register/unregister functions for particular messages
* have kill functions
* are orchestrated per process by a round-robin actor scheduler
    * get next actor in list
    * run it
    * rotate it to the end of the list, unless it's dead, then just remove it.
* communication with actors in another process via process queues
* communication with actors in another host via ssh?
* can be dispatched to another process or host explicitly or dynamically if the cpu/host is over/underutilized?
* will have to be robust to failures sending a message.  if the target actor has died, the message will cause an exception in the sender.
