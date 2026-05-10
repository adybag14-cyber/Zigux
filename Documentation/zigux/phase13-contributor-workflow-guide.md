# Phase 13 Contributor Workflow Guide

## Purpose

Use this guide when a change touches the active Phase 13 shared-helper packet and the review needs one compact contributor-facing workflow instead of scattered reminders.

This guide is for contributor workflow guidance only.
It does not create a new helper lane, a new replay count, or a new closure claim.

## Packet Boundary

Keep the current Phase 13 packet bounded to the roadmap-owned helper families:
- `fs/libfs.c`
- `lib/devres.c`
- `security/landlock/ruleset.c`
- `security/landlock/syscalls.c`

Keep notifier evidence adjacent to that packet rather than treating it as a fifth helper anchor.
The adjacent notifier evidence packet is tracked through:
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `scripts/zigux/check-phase13-notifier-packet.py`
- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `zigux/bindings/notifier_abi.zig`
- `include/zigux/abi.h`
- `include/zigux/notifier_abi.h`
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`
- `zigux/helpers/notifier_chain_view.zig`
- `drivers/tty/hvc/hvc_console.h`

## Shared Surfaces

When contributor-facing wording changes, keep these broad surfaces aligned:
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

## Workflow

1. Confirm the change stays inside one bounded Phase 13 lane.
2. Keep the owner split visible instead of collapsing `libfs`, `devres`, `landlock`, and notifier evidence into one generic summary.
3. If a broad reminder changes, reread the shared surfaces together before adding packet-local prose.
4. Keep adjacent notifier evidence explicit whenever a contributor-facing summary mentions the shared Phase 13 packet.
5. Record Phase 13 as still active and reviewable; do not imply closure or a frozen packet.

## Contributor Prompts

Use these prompts when reviewing or updating shared workflow wording:
- Does the wording keep `libfs`, `devres`, `landlock`, and adjacent notifier evidence as separate ownership buckets?
- Does the wording keep the helper-owned Landlock ruleset boundary explicit through `Documentation/zigux/phase13-landlock-ruleset-ownership.md` instead of folding that owner cue into generic syscall or release wording?
- Does the wording keep notifier evidence adjacent to the shared-helper packet rather than counting it as a fifth helper tranche?
- Does the wording stay grounded in shipped contributor-facing notes instead of hoping for future validator or replay surfaces?
- Does the wording keep the landed nonincreasing-priority signal explicit through `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/tests/phase13_notifier_list_reviewability.zig`, and `zigux/helpers/notifier_chain_view.zig`?
- Does the wording keep the packet bounded to helper-first and truthfulness work instead of widening into subsystem-implementation claims?

## Non-Goals

- This guide does not claim a closed Phase 13 tranche.
- This guide does not promote notifier evidence into a fifth shared-helper anchor.
- This guide does not widen Phase 13 into runtime HVC parity, deeper security policy scope, or unrelated release-planning work.
