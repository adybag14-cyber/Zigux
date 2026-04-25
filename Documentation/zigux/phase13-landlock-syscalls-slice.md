# Phase 13 Landlock Syscalls Slice

This bounded Phase 13 slice starts `security/landlock/syscalls.zig` with a pure helper-first foothold anchored to `security/landlock/syscalls.c`.

The current helper stays intentionally narrow:

- reports the ABI shape checks that `build_check_abi()` enforces for `landlock_ruleset_attr`, `landlock_path_beneath_attr`, and `landlock_net_port_attr`
- models the query and validation path of `landlock_create_ruleset()` around version and errata requests, minimum struct sizing, page-size bounds, handled-access mask filtering, and empty-ruleset rejection
- translates the logging and thread-sync flags used by `landlock_restrict_self()`, including the special `ruleset_fd == -1` mute-subdomains-only case

This slice does not claim anonymous-fd creation, ruleset FD lookup, path imports, rule addition, credential preparation, thread synchronization, domain merges, or live syscall enforcement.

The next honest bounded step in this same lane is to add one small in-memory planner around `landlock_add_rule()` rule-type dispatch, empty-access rejection, and net-port bounds before touching real FD validation or path resolution.
