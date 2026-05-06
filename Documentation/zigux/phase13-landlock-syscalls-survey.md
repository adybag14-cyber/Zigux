# Phase 13 Landlock Syscalls Survey

This document records the bounded Phase 13 survey lane around `security/landlock/syscalls.c`.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_LANE_KEY=P13-Y04`
- `PHASE13_SLICE=landlock-syscalls-helper-path-beneath-handoff`
- `PHASE13_SURVEYED_COMMIT=02f3325b2e289b7d492e022db0dbe7b61f2e22c3`
- scope: the landed `security/landlock/syscalls.zig` helper slice, its dedicated Phase 13 test gate and manifest, the shared Phase 13 build wiring, and the lane notes that compare the current foothold against the roadmap
- product boundary:
  - `security/landlock/syscalls.zig`
  - `zigux/tests/phase13_landlock_syscalls.zig`
  - `zigux/tests/phase13_landlock_syscalls_manifest.json`
  - `zigux/tests/phase13_build.zig`
  - `Documentation/zigux/phase13-landlock-syscalls-slice.md`
  - `Documentation/zigux/phase13-landlock-syscalls-survey.md`
  - `Documentation/zigux/phase13-landlock-syscalls-governance.md`

## Why this slice exists

The Phase 13 roadmap explicitly names `security/landlock/syscalls.c` as a shared security-helper anchor.

That matters because the live Landlock syscall anchor is already 592 lines and mixes UAPI shape checks, query handling, anonymous-fd creation, file-descriptor validation, path import, rule dispatch, credential preparation, thread synchronization, and domain merge or logging behavior.

The highest-value honest step in this lane is therefore not to pretend Zigux owns the full syscall surface. It is to keep landing reviewable helper-first planners that narrow the next real branch without widening into live FD, path, or credential state.

## Survey findings

- `security/landlock/syscalls.c` is present on `master` and spans multiple user-facing and kernel-facing boundaries at once: ABI structure sizing, query-only create-ruleset calls, ruleset file-descriptor creation, rule import, and restrict-self credential updates.
- the live repo already had the shared Phase 13 build gate and `make -C zigux phase13` target, which made it practical to add a lane-local syscall helper without widening into kernel build integration.
- the current `security/landlock/syscalls.zig` slice now stays intentionally narrow around `build_check_abi()` sizing, `landlock_create_ruleset()` query and mask validation, `landlock_restrict_self()` logging-flag translation including the special `ruleset_fd == -1` mute-subdomains-only case, the first `landlock_add_rule()` planner for rule-type dispatch and bounded rule-shape validation, the in-memory `get_ruleset_from_fd()` planner for bad-FD rejection, ruleset-FD type checks, `FMODE_CAN_WRITE` or `FMODE_CAN_READ` access checks, and the single-layer guard, the in-memory `get_path_from_fd()` planner for ruleset-FD rejection, internal-mount filtering, non-user-visible inode rejection, and owned path reference handoff, plus a new in-memory `add_rule_path_beneath()` planner that combines copied path-beneath attrs with the bounded path-FD handoff and the later `put_path()` release responsibility.
- the new helper-local governance note keeps ownership and fixture claims coupled to `SyscallsHelperLab.descriptor()` so future Phase 13 notes or fixtures cannot quietly turn this planning lab into an implied runtime wrapper while all live-surface flags remain false.
- the helper still does not claim anonymous inode creation, live FD ownership, path-backed rule import, `prepare_creds()`, thread synchronization, or live domain merges.
- the next honest syscall-facing step is one tiny planner around `fop_ruleset_release()` so the retained ruleset handoff, matching `landlock_put_ruleset()` release, and zero return contract stay explicit before any live file-operations wiring or FD ownership changes are attempted.

## Recorded gaps

The current lane state is:

- landed `phase13-build-gate`
- landed `phase13-make-target`
- landed `phase13-landlock-syscalls-starter`
- landed `phase13-landlock-syscalls-test-gate`
- landed `phase13-landlock-syscalls-slice-note`
- landed `phase13-landlock-syscalls-survey-note`
- landed `phase13-landlock-syscalls-governance-note`
- landed `phase13-landlock-add-rule-followup`
- landed `phase13-landlock-ruleset-fd-mode-followup`
- landed `phase13-landlock-path-fd-followup`
- landed `phase13-landlock-path-beneath-handoff-followup`
- ready-next `phase13-landlock-ruleset-release-followup`

This keeps the lane explicit without overstating progress: Zigux now has a real `syscalls.zig` helper foothold for ABI, create-ruleset, restrict-self, add-rule, ruleset-FD, path-FD, and path-beneath handoff planning, plus one governance note that fences ownership and fixture claims, but it still does not claim anonymous inode creation, live file-operations wiring, path import, or task enforcement.

## Non-goals

This survey slice does not claim:

- anonymous inode creation or file operations wiring
- live FD ownership or reference lifecycle
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

Stay in the Phase 13 Landlock syscalls lane and add one tiny `security/landlock/syscalls.zig` planner around `fop_ruleset_release()` next, limited to the retained ruleset in `private_data`, the matching `landlock_put_ruleset()` release, and the zero return contract before any live file-operations wiring, credential updates, or live domain state are attempted.