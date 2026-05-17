# Phase 13 Landlock Syscalls Slice

This bounded Phase 13 slice keeps `security/landlock/syscalls.zig` aligned with `security/landlock/syscalls.c` as a pure helper-first packet.

The current helper stays intentionally narrow:
  * keeps `landlock_create_ruleset()` reviewable around the ABI-version query branch, minimum attr sizing, flag validation, handled-access filtering, empty-ruleset rejection, and delegated ruleset-planning before the still-blocked anonymous-fd boundary
  * keeps the helper descriptor explicit about what is in scope today: create-ruleset planning, ABI-version query planning, handled-access validation, attr-size validation, and flag validation
  * keeps delegated ruleset creation planning explicit through `security/landlock/ruleset.zig` instead of presenting live anonymous-fd installation or returned-file-descriptor ownership as shipped Zigux behavior
  * keeps current repo reality explicit: `security/landlock/syscalls.zig`, this slice note, and `Documentation/zigux/phase13-landlock-syscalls-governance.md` are materialized on current `master`, while the direct survey, replay, reviewability, manifest, and shared `zigux/tests/phase13_build.zig` companions remain absent

This slice does not claim anonymous-fd creation, live fd installation, live path imports, credential mutation, thread synchronization, domain merges, live syscall enforcement, `landlock_restrict_self()` planning, `landlock_add_rule()` planning, or release-side wrapper ownership.
