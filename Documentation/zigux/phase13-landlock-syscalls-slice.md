# Phase 13 Landlock Syscalls Slice

This bounded Phase 13 slice starts `security/landlock/syscalls.zig` with a pure helper-first foothold anchored to `security/landlock/syscalls.c`.

- `PHASE13_OWNERSHIP_BOUNDARY=ruleset-fd-handoff-helper-only`

The current helper stays intentionally narrow:

- reports the ABI shape checks that `build_check_abi()` enforces for `landlock_ruleset_attr`, `landlock_path_beneath_attr`, and `landlock_net_port_attr`
- models the shared `is_initialized()` gate used by `landlock_create_ruleset()`, `landlock_add_rule()`, and `landlock_restrict_self()`, keeping the boot-disabled `-EOPNOTSUPP` return and warning intent explicit without touching live boot configuration or setup state
- models the `copy_min_struct_from_user()` helper discipline around null-user rejection, minimum-size and page-limit validation, plus copy-then-zero-fill intent without touching live user-memory access
- models the query and validation path of `landlock_create_ruleset()` around version and errata requests, minimum struct sizing, page-size bounds, handled-access mask filtering, and empty-ruleset rejection
- translates the logging and thread-sync flags used by `landlock_restrict_self()`, including the special `ruleset_fd == -1` mute-subdomains-only case
- adds one in-memory `landlock_restrict_self()` credential handoff planner that keeps the `task_no_new_privs()` or `CAP_SYS_ADMIN` gate, `prepare_creds()`, optional ruleset merge, optional sibling-thread synchronization, and final `commit_creds()` order explicit without touching live credentials or domain ownership
- adds one in-memory `landlock_add_rule()` planner for rule-type dispatch, empty-access rejection, handled-access subset checks, and net-port bounds without touching file descriptors or paths
- adds one in-memory `get_ruleset_from_fd()` planner for bad-FD rejection, ruleset-FD type checks, `FMODE_CAN_WRITE` or `FMODE_CAN_READ` access checks, and the single-layer guard without touching the live FD table
- adds one in-memory `get_path_from_fd()` planner for bad-FD rejection, ruleset-FD rejection, internal-mount and non-user-visible inode filtering, and owned path reference handoff without touching live paths
- adds one in-memory `add_rule_path_beneath()` planner that combines copied path-beneath attrs with the bounded `get_path_from_fd()` handoff and the later `put_path()` release responsibility without touching live rule insertion or inode ownership
- adds one in-memory `add_rule_net_port()` planner that reuses the bounded add-rule validation and makes the copied net-port attrs plus final `landlock_append_net_rule()` handoff explicit without touching live socket, ruleset, or domain state
- adds one in-memory ruleset-FD creation handoff planner that keeps the fixed `anon_inode_getfd("[landlock-ruleset]", ..., O_RDWR | O_CLOEXEC)` label or flag discipline plus the `landlock_put_ruleset()` failure release responsibility explicit without touching live file operations wiring or FD ownership
- makes the dedicated `ruleset_fops` contract explicit so the helper records the `fop_ruleset_release()` ownership drop and the dummy read or write handlers that enable `FMODE_CAN_READ` and `FMODE_CAN_WRITE` without claiming live file operations wiring
- pairs that helper-owned ruleset-FD contract with the same-family `zigux/tests/phase13_landlock_ruleset_fops_sync.zig` guard so ruleset-FD creation planning and the explicit `ruleset_fops` contract stay packet-local review evidence instead of becoming an implicit shared-build dependency
- records the ruleset-FD ownership boundary as helper-only planning: `landlock_put_ruleset()` failure release and `fop_ruleset_release()` close-time drop stay explicit here, while live FD-table ownership remains with the C implementation

This slice does not claim anonymous-fd creation, live user-memory copying, path imports, credential preparation, thread synchronization, domain merges, or live syscall enforcement.

The next honest bounded step in this same lane is to stay parked at the current syscall-helper boundary unless another follow-up can tighten validation or lifetime discipline without widening into anonymous inode internals, live FD ownership, deeper credential mutation, or domain state.
