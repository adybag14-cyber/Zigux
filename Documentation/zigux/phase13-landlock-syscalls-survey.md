# Phase 13 Landlock Syscalls Survey

This document records the bounded Phase 13 survey lane around `security/landlock/syscalls.c`.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_SLICE=landlock-syscalls-helper-pure-handoff-boundary`
- `PHASE13_SURVEYED_COMMIT=672d03034b090ab859f4088396160ea13120e1d6`
- scope: the landed `security/landlock/syscalls.zig` helper slice, its dedicated Phase 13 test gate, the new reviewability gate, the shared Phase 13 build wiring, and the lane notes that compare the current foothold against the roadmap
- product boundary:
  - `security/landlock/syscalls.zig`
  - `zigux/tests/phase13_landlock_syscalls.zig`
  - `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
  - `zigux/tests/phase13_landlock_ruleset_fops_sync.zig`
  - `zigux/tests/phase13_landlock_syscalls_manifest.json`
  - `zigux/tests/phase13_build.zig`
  - `Documentation/zigux/phase13-landlock-syscalls-slice.md`
  - `Documentation/zigux/phase13-landlock-syscalls-survey.md`

## Why this slice exists

The Phase 13 roadmap explicitly names `security/landlock/syscalls.c` as a shared security-helper anchor.

That matters because the live Landlock syscall anchor is already 592 lines and mixes UAPI shape checks, query handling, anonymous-fd creation, file-descriptor validation, path import, rule dispatch, credential preparation, thread synchronization, and domain merge or logging behavior.

The highest-value honest step in this lane is therefore not to pretend Zigux owns the full syscall surface. It is to keep landing reviewable helper-first planners that narrow the next real branch without widening into live user-memory, FD, path, credential, or network state.

## Survey findings

- `security/landlock/syscalls.c` is present on `master` and spans multiple user-facing and kernel-facing boundaries at once: ABI structure sizing, the shared `is_initialized()` boot-disabled gate, query-only create-ruleset calls, ruleset file-descriptor creation, rule import, and restrict-self credential updates.
- this survey packet is refreshed to inspected head `672d03034b090ab859f4088396160ea13120e1d6`, and the dedicated `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_ruleset_fops_sync.zig` gates remain the packet-local validation surfaces for keeping the wrapper and policy planners aligned with the bounded helper contract recorded in this lane.
- the live repo already had the shared Phase 13 build gate and `make -C zigux phase13` target, which made it practical to add a lane-local syscall helper without widening into kernel build integration.
- compared against the Phase 13 roadmap and the current repo reality, the next pure syscall-helper follow-up in this packet was the shared `is_initialized()` gate before all three public entry points, so this lane now closes that gap by making the boot-disabled `-EOPNOTSUPP` return and warning-once intent explicit without claiming boot-time configuration or live setup ownership.
- the current `security/landlock/syscalls.zig` slice now stays intentionally narrow around `build_check_abi()` sizing, the shared `is_initialized()` gate for `landlock_create_ruleset()`, `landlock_add_rule()`, and `landlock_restrict_self()`, `copy_min_struct_from_user()` helper discipline, `landlock_create_ruleset()` query and mask validation, `landlock_restrict_self()` logging-flag translation plus the later in-memory credential handoff order, the first `landlock_add_rule()` planner for rule-type dispatch and bounded rule-shape validation, the in-memory `get_ruleset_from_fd()` planner for bad-FD rejection, ruleset-FD type checks, `FMODE_CAN_WRITE` or `FMODE_CAN_READ` access checks, and the single-layer guard, the in-memory `get_path_from_fd()` planner for ruleset-FD rejection, internal-mount filtering, non-user-visible inode rejection, and owned path reference handoff, the in-memory `add_rule_path_beneath()` planner that combines copied attrs with the bounded path-FD handoff and the later `put_path()` release responsibility, the in-memory `add_rule_net_port()` planner that reuses the add-rule validation and keeps the copied net-port attrs plus `landlock_append_net_rule()` boundary explicit, plus the in-memory ruleset-FD creation and `ruleset_fops` planners that fix the anon-inode label, `O_RDWR | O_CLOEXEC` flags, `fop_ruleset_release()` ownership drop, and the dummy read or write handlers behind `FMODE_CAN_READ` and `FMODE_CAN_WRITE` without claiming live FD ownership.
- the shared replay now also carries the tiny `zigux/tests/phase13_landlock_ruleset_fops_sync.zig` guard, which cross-checks the same ruleset-FD creation and `ruleset_fops` planners against each other so that the helper-side label, mode, release, and dummy-handler contract does not quietly drift inside the shared Phase 13 build.
- the dedicated reviewability gate now ties the helper surface, manifest, survey note, the same-family `phase13_landlock_ruleset_fops_sync.zig` evidence, and shared Phase 13 build wiring together so future runs can detect drift in this syscall packet before widening into live file-descriptor or credential state.
- the helper still does not claim anonymous inode creation internals, live user-memory access, live FD ownership, path-backed or port-backed rule insertion, live `prepare_creds()` mutation, live sibling-thread synchronization, or live domain merges.
- after this broader pure handoff-boundary slice, the next honest syscall-facing move is to stay parked unless another tiny validation-only or lifetime-discipline follow-up can remain pure without widening into anonymous inode internals, live user-memory access, live FD ownership, deeper credential mutation, or domain state.

## Recorded gaps

The current lane state is:

- landed `phase13-build-gate`
- landed `phase13-make-target`
- landed `phase13-landlock-syscalls-starter`
- landed `phase13-landlock-syscalls-test-gate`
- landed `phase13-landlock-syscalls-reviewability-gate`
- landed `phase13-landlock-syscalls-slice-note`
- landed `phase13-landlock-syscalls-survey-note`
- landed `phase13-landlock-initialization-gate-followup`
- landed `phase13-landlock-copy-min-struct-followup`
- landed `phase13-landlock-add-rule-followup`
- landed `phase13-landlock-ruleset-fd-mode-followup`
- landed `phase13-landlock-path-fd-followup`
- landed `phase13-landlock-path-beneath-handoff-followup`
- landed `phase13-landlock-net-port-import-followup`
- landed `phase13-landlock-ruleset-fd-creation-handoff-followup`
- landed `phase13-landlock-restrict-self-credential-handoff-followup`
- landed `phase13-landlock-ruleset-fops-followup`

This keeps the lane explicit without overstating progress: Zigux now has a real `syscalls.zig` helper foothold for ABI, the shared initialization gate, bounded user-struct copy discipline, create-ruleset, restrict-self flag translation, restrict-self credential handoff ordering, add-rule, ruleset-FD lookup, path-FD lookup, path-beneath handoff, net-port handoff, ruleset-FD creation handoff, the dedicated ruleset file-operations contract, and a manifest-backed reviewability gate, but it still does not claim anonymous inode creation internals, live user-memory access, live path or port import, or task enforcement.

## Non-goals

This survey slice does not claim:

- anonymous inode creation internals or live file operations wiring
- live user-memory copying
- live FD ownership or reference lifecycle
- path-backed or port-backed rule import
- credential allocation, replacement, or rollback
- sibling thread synchronization
- domain merge or hierarchy mutation
- live syscall enforcement

## Gates

1. run the focused syscall helper checks
- `zig test security/landlock/syscalls.zig`
- `zig test --dep landlock_syscalls -Mroot=zigux/tests/phase13_landlock_syscalls.zig -Mlandlock_syscalls=security/landlock/syscalls.zig`
- `zig test --dep landlock_syscalls -Mroot=zigux/tests/phase13_landlock_syscalls_reviewability.zig -Mlandlock_syscalls=security/landlock/syscalls.zig`
- `zig test --dep landlock_syscalls -Mroot=zigux/tests/phase13_landlock_ruleset_fops_sync.zig -Mlandlock_syscalls=security/landlock/syscalls.zig`

2. run the dedicated Phase 13 build
- `zig build test --build-file zigux/tests/phase13_build.zig`

3. run the convenience target
- `make -C zigux phase13`

## Next bounded step

Stay in the Phase 13 Landlock syscalls lane only if another tiny `security/landlock/syscalls.zig` follow-up can tighten validation or lifetime discipline while staying pure; otherwise leave this helper parked at the current syscall boundary instead of widening into anonymous inode internals, live user-memory access, FD ownership, deeper credential mutation, or domain state.
