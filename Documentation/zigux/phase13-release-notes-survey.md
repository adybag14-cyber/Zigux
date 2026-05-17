# Phase 13 Release Notes Survey

## Purpose

This note keeps the shared Phase 13 release summary honest against the live current-`master` packet.

It is a release-surface survey only. It does not claim a closed tranche, a new replay route, or a broader shipped helper packet than the current tree can actually materialize.

## Roadmap Fit

Phase 13 in the Zigux roadmap stays bounded to four shared-helper anchors:

- `fs/libfs.c`
- `lib/devres.c`
- `security/landlock/ruleset.c`
- `security/landlock/syscalls.c`

Broad release wording should stay tied to those four anchors instead of collapsing them into one generic Phase 13 bucket or promoting adjacent notifier evidence into a fifth helper family.

## Current Shared Reminder Surfaces

Direct current-`master` readback in this run materialized these shared reminder surfaces:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-shared-summary-guard-gap.md`
- `Documentation/zigux/phase13-notifier-summary-gap.md`
- `scripts/zigux/check-phase13-tests-readme-alignment.py`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

Those files keep the shared Phase 13 packet active, helper-backed, and still not closed, while the reminder surface stays broader than any one helper-local packet.

Current `master` also keeps the helper-local packet split visible from the release surface:

- `libfs` stays anchored through `Documentation/zigux/phase13-libfs-survey.md`, `fs/libfs.zig`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, and `zigux/tests/phase13_libfs_manifest.json`
- `devres` stays anchored through `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `lib/devres.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, and `zigux/tests/phase13_devres_boundary_evidence.zig`, and `zigux/tests/phase13_devres_manifest.json`
- `landlock/ruleset` and `landlock/syscalls` stay helper-local through their ownership, slice, survey, source, and manifest-backed replay surfaces rather than collapsing into docs-only governance metadata
- adjacent notifier evidence remains support material rather than a fifth roadmap anchor

## Current Shared Release Handle

The release-planning handle that is directly supportable from this run stays anchored to the materialized reminder surfaces:

- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`

Keep broad release wording tied to that reminder packet while the missing validator-first helpers and missing shared build wrapper surfaces remain explicit repo-reality gaps.

## Repo-Reality Gaps

Direct current-`master` readback in this run still returned missing for:

- `scripts/zigux/validate-phase13-release.py`
- `zigux/Makefile`
- `zigux/tests/phase13_build.zig`
- `scripts/zigux/check-phase13-devres-packet-alignment.py`
- `scripts/zigux/check-phase13-landlock-ruleset-packet.py`
- `scripts/zigux/check-phase13-notifier-priority-signal.py`
- `scripts/zigux/check-phase13-shared-summary-surfaces.py`

Keep those paths framed as repo-reality gaps instead of presenting them as a stable shared Phase 13 release handle.

Keep older or still-missing direct companions explicit too instead of promoting them into shipped current-`master` evidence when they are not freshly reread in the same run.

## Release-Surface Posture

Keep Phase 13 release wording inside these boundaries:

- the Phase 13 packet is active and roadmap-backed, not closed
- the shared packet is helper-local and reminder-surface backed rather than validator-first in the current direct-readback posture
- the shared release handle is the materialized docs-root, scripts-root, and tests-root reminder packet listed above
- the missing validator-first helpers, shared build companion, and shared wrapper surfaces stay explicit as repo-reality gaps
- adjacent notifier evidence may still matter for release truthfulness, but it does not become a fifth roadmap anchor
- contributor-facing reminder edits in this lane should stay narrow and should not reopen helper implementation, checker code, or tranche-closure claims

## Re-Read Before Updating This Note Again

When this survey changes, reread these shared reminder surfaces together first:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-shared-summary-guard-gap.md`
- `Documentation/zigux/phase13-notifier-summary-gap.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `scripts/zigux/check-phase13-tests-readme-alignment.py`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

Only widen beyond this survey if a fresh current-`master` reread shows that one of those coupled reminder surfaces cannot stay truthful without the adjacent same-lane follow-through.

## Non-Goals

- This note does not claim a stable validator-first handle on current `master`.
- This note does not claim shipped helper-local parity beyond the directly reread packet.
- This note does not widen into notifier implementation, checker repair, or helper-local tranche closure.
