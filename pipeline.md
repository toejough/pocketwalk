watch pocketwalk config

on change:
* update valid tools
* ensure those tools (and only those tools) have results recorded for them
* update config paths
* ensure those paths (and only those paths) are being watched
* update tool config

watch config paths | watch tool config

on change:
* update paths to run, trigger paths
* ensure those paths (and only those paths) are being watched

watch paths to run | watch trigger paths | watch tool config | watch tool results

on change:
* update tools to run, with what config
* ensure the tools to run (and only tools to run) are running or have completed

watch stop signal | watch single run complete

on stop or single run complete:
* clear tools to run
* stop tools
* stop watchers
* return 0 if no tools stopped & last state was pass
* return 1 if tools were stopped or last state was not pass
