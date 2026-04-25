# Phase 13 Landlock Syscalls Survey

This document records the bounded Phase 13 survey lane around `security/landlock/syscalls.c`.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_SLICE=landlock-syscalls-helper-starter`
- scope: the landed `security/landlock/syscalls.zig` helper starter, its dedicated Phase 13 test gate and manifest, the shared Phase 13 build wiring, and the lane notes that compare the new foothold against the roadmap
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

The highest-value honest step in this lane is therefore not to pretend Zigux owns the full syscall surface. It is to start with the ABI and flag-planning helpers that are reviewable in isolation, then keep the remaining FD, path, and credential work explicit.

## Survey findings

- `security/landlock/syscalls.c` is present on `master` and spans multiple user-facing and kernel-facing boundaries at once: ABI structure sizing, query-only create-ruleset calls, ruleset file-descriptor creation, rule import, and restrict-self credential updates.
- the live repo already had the shared Phase 13 build gate and `make -C zigux phase13` target, which made it practical to add a lane-local syscall helper without widening into kernel build integration.
- the new `security/landlock/syscalls.zig` starter stays intentionally narrow around `build_check_abi()` sizing, `landlock_create_ruleset()` query and mask validation, and `landlock_restrict_self()` logging-flag translation.
- the starter does not claim anonymous inode creation, FD ownership, path-backed rule import, `landlock_add_rule()` behavior, `prepare_creds()`, thread synchronization, or live domain merges.
- the next honest syscall-facing step is one small planner around `landlock_add_rule()` rule-type dispatch and rule-shape validation, still in-memory and still outside real FD or path handling.

## Recorded gaps

The current lane state is:

- landed `phase13-build-gate`
- landed `phase13-make-target`
- landed `phase13-landlock-syscalls-starter`
- landed `phase13-landlock-syscalls-test-gate`
- landed `phase13-landlock-syscalls-slice-note`
- landed `phase13-landlock-syscalls-survey-note`
- ready-next `phase13-landlock-add-rule-followup`
- blocked `phase13-landlock-live-fd-path-and-cred-state`

This keeps the lane explicit without overstating progress: Zigux now has a real `syscalls.zig` helper foothold for ABI and syscall-flag planning, but it still does not claim live Landlock FD plumbing, rule import, or task enforcement.

## Non-goals

This survey slice does not claim:

- anonymous inode creation or file operations wiring
- ruleset FD lookup or access-mode validation
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

Stay in the Phase 13 Landlock syscalls lane and add one tiny `security/landlock/syscalls.zig` add-rule planner next, limited to `landlock_add_rule()` rule-type dispatch, empty-access rejection, and net-port bounds before any real ruleset FD validation, path resolution, or credential updates are attempted.
