# Phase 13 Landlock Syscalls Slice

This bounded Phase 13 slice keeps `security/landlock/syscalls.zig` aligned with `security/landlock/syscalls.c` as a pure helper-first packet.

The current helper stays intentionally narrow:
  * keeps `landlock_create_ruleset()` reviewable around the `build_check_abi()` shape checks, query-versus-create dispatch, minimum attr sizing, page-size bounds, handled-access filtering, and empty-ruleset rejection before the still-blocked anonymous-fd boundary
  * keeps `landlock_restrict_self()` explicit around the `no_new_privs` versus `CAP_SYS_ADMIN` credential gate, the current logging-flag translation, and the detached `ruleset_fd = -1` plus `LANDLOCK_RESTRICT_SELF_LOG_SUBDOMAINS_OFF` update path
  * keeps `landlock_add_rule()` planning bounded to the `path_beneath` and `net_port` branches with ruleset-write and path-or-port handoff checks
  * keeps `fop_ruleset_release()` explicit as the release-side ownership drop
  * keeps the combined `ruleset_fops` wrapper contract explicit through `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
  * keeps the missing shared `zigux/tests/phase13_build.zig` route explicit instead of implying that the older shared build bundle has returned

This slice does not claim anonymous-fd creation, live fd installation, live path imports, credential mutation, thread synchronization, domain merges, or live syscall enforcement.
