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

Broad summaries should also keep the bounded `devres` dma/scatterlist release evidence visible through:
- `zigux/tests/phase13_devres_manifest.json`
- `zigux/tests/phase13_devres_reviewability.zig`
- `zigux/tests/phase13_devres_dma_coherent.zig`
- `zigux/tests/phase13_devres_boundary_evidence.zig`
- `scripts/zigux/check-phase13-devres-packet.py`

Broad summaries should also keep the adjacent notifier evidence packet visible through:
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `zigux/bindings/notifier_abi.zig`
- `include/zigux/abi.h`
- `include/zigux/notifier_abi.h`
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`
- `zigux/helpers/notifier_chain_view.zig`
- `drivers/tty/hvc/hvc_console.h`

## Release-Surface Posture

Keep Phase 13 release wording inside these boundaries:
- the shared-helper packet is active rather than closed
- `devres` dma/scatterlist evidence stays inside the active helper packet rather than reading like a separate replay lane
- notifier evidence stays adjacent release-surface support rather than a fifth helper lane
- contributor-facing notes should prefer one bounded wording repair at a time
- broad summaries should stay grounded in the shipped docs packet rather than speculative future closure language

## Where To Re-Read Before Updating Release Wording

Refresh these notes together when a contributor-facing Phase 13 summary changes:
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-notifier-list-survey.md`

## Non-Goals

- This note does not claim a new shared replay route.
- This note does not collapse the owner split into one generic Phase 13 helper bucket.
- This note does not claim HVC runtime parity or a broader notifier subsystem delivery.
