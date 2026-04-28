# Phase 13 Landlock Syscalls Survey

This document records the bounded Phase 13 survey lane around `security/landlock/syscalls.c`.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_SLICE=landlock-syscalls-helper-ruleset-fd-creation-handoff`
- `PHASE13_SURVEYED_COMMIT=05a762ea272fa488b877178987418c54c030b239`
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

The highest-value honest step in this lane is therefore not to pretend Zigux owns the full syscall surface. It is to keep landing reviewable helper-first planners that narrow the next real branch without widening into live FD, path, credential, or network state.

## Survey findings

- `security/landlock/syscalls.c` is present on `master` and spans multiple user-facing and kernel-facing boundaries at once: ABI structure sizing, query-only create-ruleset calls, ruleset file-descriptor creation, rule import, and restrict-self credential updates.
- a focused attached-toolchain check still compiles and passes the dedicated `zigux/tests/phase13_landlock_syscalls.zig` gate at inspected head `05a762ea272fa488b877178987418c54c030b239`, so the current wrapper and policy planners remain aligned with the bounded helper contract recorded in this lane packet.
- the live repo already had the shared Phase 13 build gate and `make -C zigux phase13` target, which made it practical to add a lane-local syscall helper without widening into kernel build integration.
- compared against the Phase 13 roadmap and the current repo reality, the highest-value bounded gap was the next tiny lifetime-discipline branch still missing from the live helper slice: one planner around the ruleset-FD creation handoff at `anon_inode_getfd("[landlock-ruleset]", &ruleset_fops, ruleset, O_RDWR | O_CLOEXEC)`.
- the current `security/landlock/syscalls.zig` slice now stays intentionally narrow around `build_check_abi()` sizing, `landlock_create_ruleset()` query and mask validation, `landlock_restrict_self()` logging-flag translation, the first `landlock_add_rule()` planner for rule-type dispatch and bounded rule-shape validation, the in-memory `get_ruleset_from_fd()` planner for bad-FD rejection, ruleset-FD type checks, `FMODE_CAN_WRITE` or `FMODE_CAN_READ` access checks, and the single-layer guard, the in-memory `get_path_from_fd()` planner for ruleset-FD rejection, internal-mount filtering, non-user-visible inode rejection, and owned path reference handoff, the in-memory `add_rule_path_beneath()` planner that combines copied attrs with the bounded path-FD handoff and the later `put_path()` release responsibility, the in-memory `add_rule_net_port()` planner that reuses the add-rule validation and keeps the copied net-port attrs plus `landlock_append_net_rule()` boundary explicit, plus a new in-memory ruleset-FD creation handoff planner that fixes the anon-inode label, `O_RDWR | O_CLOEXEC` flags, and the `landlock_put_ruleset()` failure release discipline without claiming live file operations wiring or FD ownership.
- the helper still does not claim anonymous inode creation, live FD ownership, path-backed or port-backed rule insertion, `prepare_creds()`, thread synchronization, or live domain merges.
- after this ruleset-FD creation handoff slice, the next honest syscall-facing move is to stay parked unless another tiny validation or lifetime-discipline follow-up can remain pure without widening into anonymous inode internals, live FD ownership, credential updates, or domain state.

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
- landed `phase13-landlock-path-fd-followup`
- landed `phase13-landlock-path-beneath-handoff-followup`
- landed `phase13-landlock-net-port-import-followup`
- landed `phase13-landlock-ruleset-fd-creation-handoff-followup`

This keeps the lane explicit without overstating progress: Zigux now has a real `syscalls.zig` helper foothold for ABI, create-ruleset, restrict-self, add-rule, ruleset-FD lookup, path-FD lookup, path-beneath handoff, net-port handoff, and ruleset-FD creation handoff planning, but it still does not claim anonymous inode creation internals, live path or port import, or task enforcement.

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

Stay in the Phase 13 Landlock syscalls lane only if another tiny `security/landlock/syscalls.zig` follow-up can tighten validation or lifetime discipline while staying pure; otherwise leave this helper parked at the current syscall boundary instead of widening into anonymous inode internals, FD ownership, credential updates, or domain state.
