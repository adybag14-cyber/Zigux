# Phase 13 Landlock Syscalls Slice

This bounded Phase 13 slice starts `security/landlock/syscalls.zig` with a pure helper-first foothold anchored to `security/landlock/syscalls.c`.

The current helper stays intentionally narrow:
  * keeps the `landlock_restrict_self()` credential gate explicit by splitting reviewable planning between `CredentialGate.no_new_privs` and `CredentialGate.cap_sys_admin_override` without claiming live credential mutation
  * keeps the current restrict-self logging flags explicit by translating `LANDLOCK_RESTRICT_SELF_LOG_SAME_EXEC_OFF`, `LANDLOCK_RESTRICT_SELF_LOG_NEW_EXEC_ON`, and `LANDLOCK_RESTRICT_SELF_LOG_SUBDOMAINS_OFF` into helper-visible booleans, including the detached `ruleset_fd = -1` plus subdomains-only logging-update path
  * keeps `landlock_add_rule()` reviewable through a bounded `path_beneath` versus `net_port` split, explicit ruleset-write access validation, and separate parent-fd versus port handoff cues
  * keeps the release-side `fop_ruleset_release()` lifetime drop explicit through `planFopRulesetRelease()` without claiming live ruleset ownership transfer or anonymous-inode registration
  * keeps the combined `ruleset_fops` wrapper contract explicit through `planRulesetFops()`, including `FMODE_CAN_READ`, `FMODE_CAN_WRITE`, and the shared invalid read or write stub outcome
  * adds a direct helper-local replay packet through `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` so the shipped syscall helper packet stays machine-checkable while the older shared `zigux/tests/phase13_build.zig` surface remains absent on current `master`

This slice does not claim live credential mutation, live ruleset ownership, live file-descriptor installation, live file-operations registration, or live syscall enforcement.

The next honest bounded step in this same lane is to keep the packet truthfulness reviewable by rereading `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, `zigux/tests/phase13_landlock_syscalls.zig`, and `zigux/tests/phase13_landlock_syscalls_reviewability.zig` together before widening into anonymous-inode internals, live FD installation, or broader credential and ruleset state.
