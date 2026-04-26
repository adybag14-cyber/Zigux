# Phase 13 Landlock Syscalls Survey

This document records the bounded Phase 13 survey lane around `security/landlock/syscalls.c`.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_SLICE=landlock-syscalls-helper-starter`
- scope: the landed `security/landlock/syscalls.zig` helper slice, its dedicated Phase 13 test gate and manifest, the shared Phase 13 build wiring, and the lane notes that compare the current foothold against the roadmap
- product boundary:
  - `security/landlock/syscalls.zig`
  - `zigux/tests/phase13_landlock_syscalls.zig`
  - `zigux/tests/phase13_landlock_syscalls_manifest.json`
  - `zigux/tests/phase13_build.zig`
  - `Documentation/zigux/phase13-landlock-syscalls-slice.md`
  - `Documentation/zigux/phase13-landlock-syscalls-survey.md`

## Why this slice exists

The Phase 13 roadmap explicitly names `security/landlock/syscalls.c` as a shared security-helper anchor.

That matters because the live Landlock syscall anchor is already 592 lines and mixes UAPI shape checks, query handling, anonymous-fd creation, file-descriptor validation, path import, rule dispatch, credential preparation, thread synchronization, and domain merge or logging behavior.

The highest-value honest step in this lane is therefore not to pretend Zigux owns the full syscall surface. It is to keep landing reviewable helper-first planners that narrow the next real branch without widening into live FD, path, or credential state.

## Survey findings

- `security/landlock/syscalls.c` is present on `master` and spans multiple user-facing and kernel-facing boundaries at once: ABI structure sizing, query-only create-ruleset calls, ruleset file-descriptor creation, rule import, and restrict-self credential updates.
- the live repo already had the shared Phase 13 build gate and `make -C zigux phase13` target, which made it practical to add a lane-local syscall helper without widening into kernel build integration.
- the current `security/landlock/syscalls.zig` slice now stays intentionally narrow around `build_check_abi()` sizing, `landlock_create_ruleset()` query and mask validation, `landlock_restrict_self()` logging-flag translation, the first `landlock_add_rule()` planner for rule-type dispatch and bounded rule-shape validation, and a new `get_ruleset_from_fd()` planner for ruleset-file type, required access mode, and single-layer validation.
- the helper still does not claim anonymous inode creation, live FD ownership, `get_path_from_fd()`, path-backed rule import, `prepare_creds()`, thread synchronization, or live domain merges.
- the next honest syscall-facing step is one small planner around `get_path_from_fd()` parent-FD rejection checks for ruleset files, `MNT_INTERNAL`, and `SB_NOUSER`, still in-memory and still outside real path or credential handling.

## Recorded gaps

The current lane state is:

- landed `phase13-build-gate`
- landed `phase13-make-target`
- landed `phase13-landlock-syscalls-starter`
- landed `phase13-landlock-syscalls-test-gate`
- landed `phase13-landlock-syscalls-slice-note`
- landed `phase13-landlock-syscalls-survey-note`
- landed `phase13-landlock-add-rule-followup`
- landed `phase13-landlock-ruleset-fd-mode-followup`
- ready-next `phase13-landlock-parent-path-fd-followup`

This keeps the lane explicit without overstating progress: Zigux now has a real `syscalls.zig` helper foothold for ABI, create-ruleset, restrict-self, add-rule, and ruleset-FD planning, but it still does not claim live Landlock path import, credential mutation, or task enforcement.

## Non-goals

This survey slice does not claim:

- anonymous inode creation or file operations wiring
- live ruleset FD lookup or owned reference management
- path-backed or port-backed rule import
- credential allocation, replacement, or rollback
- sibling thread synchronization
- domain merge or hierarchy mutation
- live syscall enforcement

## Gates

1. run the dedicated Phase 13 build
- `zig build test --build-file zigux/tests/phase13_build.zig`

2. run the convenience target
- `make -C zigux phase13`

## Next bounded step

Stay in the Phase 13 Landlock syscalls lane and add one tiny `security/landlock/syscalls.zig` parent-path-FD planner next, limited to `get_path_from_fd()` rejection of ruleset FDs, `MNT_INTERNAL`, and `SB_NOUSER` before any path import, rule append, credential updates, or live domain state are attempted.
