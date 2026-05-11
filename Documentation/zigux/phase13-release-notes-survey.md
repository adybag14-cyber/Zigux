# Phase 13 Release Notes Survey

## Purpose

This note keeps the contributor-facing release summary for the active Phase 13 shared-helper packet honest.

It is a release-surface note, not a new replay lane.

## What The Broad Release Summary Must Keep Visible

The current Phase 13 packet stays centered on four roadmap-owned helper families:
- `fs/libfs.c`
- `lib/devres.c`
- `security/landlock/ruleset.c`
- `security/landlock/syscalls.c`

Broad summaries should keep the active shared-helper release handle visible through:
- `Documentation/zigux/README.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `scripts/zigux/validate-phase13-release.py`
- `zigux/tests/phase13_build.zig`
- `zigux/Makefile`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`

Broad summaries should also keep the direct devres packet visible through:
- `Documentation/zigux/phase13-devres-survey.md`
- `zigux/tests/phase13_devres.zig`
- `zigux/tests/phase13_devres_manifest.json`
- `zigux/tests/phase13_devres_reviewability.zig`
- `zigux/tests/phase13_devres_dma_coherent.zig`
- `zigux/tests/phase13_devres_boundary_evidence.zig`
- `scripts/zigux/check-phase13-devres-packet.py`

If one of those direct devres companions stops materializing on current `master`, broad summaries should record that path as repo-reality gaps rather than independently shipped current-`master` evidence.

Broad summaries should also keep the adjacent direct-evidence shards visible without counting them as extra shared replay steps:
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `scripts/zigux/check-phase13-notifier-priority-signal.py`
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
- `zigux/tests/phase13_libfs_addressability.zig`

## Release-Surface Posture

Keep Phase 13 release wording inside these boundaries:
- the shared-helper packet is active rather than closed
- the validator-first release handle stays grounded in `Documentation/zigux/README.md`, `scripts/zigux/check-phase13-devres-packet.py`, `scripts/zigux/validate-phase13-release.py`, `zigux/tests/phase13_build.zig`, `zigux/Makefile`, `make -C zigux phase13-validate`, and `make -C zigux phase13`
- direct devres companions should stay visible as shipped current-`master` evidence while adjacent notifier ABI, helper, tests-root, and HVC header companions remain repo-reality reminders until current `master` materializes them
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig` and `zigux/tests/phase13_libfs_addressability.zig` stay adjacent direct evidence rather than extra shared replay steps
- notifier evidence stays adjacent release-surface support rather than a fifth helper lane
- contributor-facing notes should prefer one bounded wording repair at a time
- broad summaries should stay grounded in the shipped docs packet rather than speculative future closure language
- adjacent notifier wording should keep the shipped notifier priority-signal checker explicit when that packet changes

## Where To Re-Read Before Updating Release Wording

Refresh these notes together when a contributor-facing Phase 13 summary changes:
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `scripts/zigux/check-phase13-devres-packet.py`
- `scripts/zigux/check-phase13-notifier-priority-signal.py`
- `scripts/zigux/validate-phase13-release.py`

## Non-Goals

- This note does not claim a new shared replay route.
- This note does not collapse the owner split into one generic Phase 13 helper bucket.
- This note does not claim HVC runtime parity or a broader notifier subsystem delivery.
