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
- `scripts/zigux/check-phase13-notifier-priority-signal.py`
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
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

Treat `make -C zigux phase13-validate` as the stable contributor-facing replay handle.
If a direct `scripts/zigux/validate-phase13-release.py` or `scripts/zigux/check-phase13-*.py` path cannot be materialized on current `master`, record that gap as repo reality instead of presenting the missing script as independently shipped reviewer evidence.

## Current Repo Reality

As of `2026-05-11`, current `master` still does not materialize these direct Phase 13 companions:
- `zigux/tests/phase13_build.zig`
- `zigux/tests/phase13_libfs.zig`
- `zigux/tests/phase13_libfs_addressability.zig`
- `zigux/tests/phase13_libfs_reviewability.zig`
- `zigux/tests/phase13_devres.zig`
- `zigux/tests/phase13_devres_reviewability.zig`
- `zigux/tests/phase13_devres_dma_coherent.zig`
- `zigux/tests/phase13_devres_boundary_evidence.zig`
- `zigux/tests/phase13_landlock_ruleset.zig`
- `zigux/tests/phase13_landlock_syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
- `scripts/zigux/check-phase13-devres-packet.py`

When a shared reminder or reviewer prompt still names any of those paths, treat that wording as contributor-guidance drift to repair instead of as shipped current-`master` evidence.

## Broad-Surface Repair Order

When current `master` still carries the repo-reality gaps above and one of the broad shared reminders drifts anyway, repair the shared contributor packet in this order:
1. `Documentation/zigux/README.md`
2. `zigux/tests/README.md`
3. `Documentation/zigux/review-checklist.md`
4. `scripts/zigux/README.md`

Use the narrower Phase 13 notes as the truth anchors while repairing those broad reminders:
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`

Do not reopen packet-local Phase 13 notes just because a broad reminder drifted.
Only widen the repair beyond those broad surfaces when current `master` readback proves the underlying repo reality changed.

## Workflow

1. Confirm the change stays inside one bounded Phase 13 lane.
2. Keep the owner split visible instead of collapsing `libfs`, `devres`, `landlock`, and notifier evidence into one generic summary.
3. If a broad reminder changes, reread the shared surfaces together before adding packet-local prose.
4. Before naming a direct scripts-root checker as review evidence, verify that the exact path is still present on current `master`; if it is not, keep the wording anchored to the shipped docs-root, tests-root, and `make -C zigux phase13-validate` surfaces and note the missing script as a blocker.
5. Before naming a direct helper-local tests-root companion as review evidence, verify that the exact path is still present on current `master`; if it is not, keep the wording anchored to the shipped docs-root, tests-root, and `make -C zigux phase13-validate` surfaces and note the missing direct companion as repo reality.
6. Keep adjacent notifier evidence explicit whenever a contributor-facing summary mentions the shared Phase 13 packet.
7. Record Phase 13 as still active and reviewable; do not imply closure or a frozen packet.

## Contributor Prompts

Use these prompts when reviewing or updating shared workflow wording:
- Does the wording keep `libfs`, `devres`, `landlock`, and adjacent notifier evidence as separate ownership buckets?
- Does the wording keep the helper-owned Landlock ruleset boundary explicit through `Documentation/zigux/phase13-landlock-ruleset-ownership.md` instead of folding that owner cue into generic syscall or release wording?
- Does the wording keep the helper-owned Landlock syscalls governance boundary explicit through `Documentation/zigux/phase13-landlock-syscalls-governance.md` instead of folding that owner cue into generic ruleset, notifier, or release wording?
- Does the wording keep notifier evidence adjacent to the shared-helper packet rather than counting it as a fifth helper tranche?
- Does the wording stay grounded in shipped contributor-facing notes instead of hoping for future validator or replay surfaces?
- Does the wording avoid presenting a direct `scripts/zigux/validate-phase13-release.py` or `scripts/zigux/check-phase13-*.py` path as independently shipped reviewer evidence when that exact file cannot be materialized on current `master`?
- Does the wording keep the currently missing direct `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_addressability.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_landlock_ruleset.zig`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `scripts/zigux/check-phase13-devres-packet.py` paths framed as repo-reality gaps instead of shipped evidence?
- Does the wording keep the landed nonincreasing-priority signal explicit through `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/tests/phase13_notifier_list_reviewability.zig`, and `zigux/helpers/notifier_chain_view.zig`?
- Does the wording keep the packet bounded to helper-first and truthfulness work instead of widening into subsystem-implementation claims?
- If broad shared reminders drifted, did the repair start with `Documentation/zigux/README.md`, then `zigux/tests/README.md`, then `Documentation/zigux/review-checklist.md`, and then `scripts/zigux/README.md` before reopening packet-local notes?

## Non-Goals

- This guide does not claim a closed Phase 13 tranche.
- This guide does not promote notifier evidence into a fifth shared-helper anchor.
- This guide does not widen Phase 13 into runtime HVC parity, deeper security policy scope, or unrelated release-planning work.
