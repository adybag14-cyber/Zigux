# Phase 13 Landlock Syscalls Slice

This bounded Phase 13 slice starts `security/landlock/syscalls.zig` with a pure helper-first foothold anchored to `security/landlock/syscalls.c`.

The current helper stays intentionally narrow:

- reports the ABI shape checks that `build_check_abi()` enforces for `landlock_ruleset_attr`, `landlock_path_beneath_attr`, and `landlock_net_port_attr`
- models the query and validation path of `landlock_create_ruleset()` around version and errata requests, minimum struct sizing, page-size bounds, handled-access mask filtering, and empty-ruleset rejection
- translates the logging and thread-sync flags used by `landlock_restrict_self()`, including the special `ruleset_fd == -1` mute-subdomains-only case
- adds one in-memory `landlock_add_rule()` planner for rule-type dispatch, empty-access rejection, handled-access subset checks, and net-port bounds without touching file descriptors or paths
- adds one in-memory `get_ruleset_from_fd()` planner for bad-FD rejection, ruleset-FD type checks, `FMODE_CAN_WRITE` or `FMODE_CAN_READ` access checks, and the single-layer guard without touching the live FD table
- adds one in-memory `get_path_from_fd()` planner for bad-FD rejection, ruleset-FD rejection, internal-mount and non-user-visible inode filtering, and owned path reference handoff without touching live paths
- adds one in-memory `add_rule_path_beneath()` planner that combines copied path-beneath attrs with the bounded `get_path_from_fd()` handoff and the later `put_path()` release responsibility without touching live rule insertion or inode ownership
- adds one in-memory `ruleset_fops` planner that keeps `fop_ruleset_release()` plus the dummy read-or-write `FMODE_CAN_READ` or `FMODE_CAN_WRITE` enablement and shared `-EINVAL` return contract explicit without wiring anonymous inode creation, live file operations, or FD ownership

This slice does not claim anonymous-fd creation, path imports, credential preparation, thread synchronization, domain merges, or live syscall enforcement.

The next honest bounded step is to keep this packet parked unless a future Phase 13 syscalls run can add another equally small planner without widening into live file-operations wiring, credential updates, or domain state.
