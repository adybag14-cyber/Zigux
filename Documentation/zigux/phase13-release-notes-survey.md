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
- `scripts/zigux/check-phase13-shared-summary-surfaces.py`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

Those files keep the shared Phase 13 packet active and still not closed. Current `master` now also keeps the old missing-checker gap closed through `Documentation/zigux/phase13-shared-summary-guard-gap.md` and `scripts/zigux/check-phase13-shared-summary-surfaces.py`, while broader docs-root follow-through stays a separate same-lane reread instead of part of the shared-summary guard gap.

Direct current-`master` rereads in this run show that `Documentation/zigux/phase13-release-coordination-matrix.md` and this survey keep the release-facing `devres` packet narrowed to `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `Documentation/zigux/phase13-devres-scatterlist-slice.md`, `scripts/zigux/check-phase13-devres-dma-boundary.py`, `scripts/zigux/check-phase13-devres-mmio-packet.py`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `zigux/tests/phase13_devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist_build.zig`.

At the same time, fresh direct readback now resolves the older reminder drift into one aligned shared-summary packet plus any separate docs-root reread that may still be needed. `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, and `zigux/tests/phase13_devres_dma_coherent.zig` confirm that the helper-local packet includes the direct DMA-boundary replay beside the planner and scatterlist packet, and the same rereads keep `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` aligned with that narrower direct `devres` packet while still treating `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` as repo-reality gaps rather than shipped evidence.

Keep this survey truthful about that now-aligned shared-summary packet instead of replaying the older broader drift claim.

Current `master` also keeps the helper-local packet split visible from the release surface:

- `libfs` stays anchored through `Documentation/zigux/phase13-libfs-survey.md`, `fs/libfs.zig`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, and `zigux/tests/phase13_libfs_manifest.json`
- `devres` stays anchored through `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `scripts/zigux/check-phase13-devres-dma-boundary.py`, `scripts/zigux/check-phase13-devres-mmio-packet.py`, `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `Documentation/zigux/phase13-devres-scatterlist-slice.md`, `lib/devres_scatterlist.zig`, `zigux/tests/phase13_devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist_build.zig`, while older `lib/devres.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_manifest.json`, `scripts/zigux/check-phase13-devres-packet.py`, and `scripts/zigux/check-phase13-devres-packet-alignment.py` stay explicit repo-reality gaps
- `landlock/ruleset` stays helper-local through its ownership, slice, survey, source, and manifest-backed replay surfaces, while `landlock/syscalls` stays helper-local through its governance note, slice, and source starter without collapsing into docs-only governance metadata
- adjacent notifier evidence remains support material rather than a fifth roadmap anchor

## Current Shared Release Handle

The release-planning handle that is directly supportable from this run stays anchored to the materialized reminder surfaces:

- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-shared-summary-guard-gap.md`
- `scripts/zigux/check-phase13-shared-summary-surfaces.py`

Keep broad release wording tied to that reminder packet while the missing validator-first helpers and missing shared build route surfaces remain explicit repo-reality gaps, and while any broader docs-root follow-through stays recorded as a separate same-lane reread instead of being restated as already-open shared-surface drift.

## Repo-Reality Gaps

Direct current-`master` readback in this run still returned missing for:

- `scripts/zigux/validate-phase13-release.py`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`
- `zigux/tests/phase13_build.zig`
- `scripts/zigux/check-phase13-devres-packet-alignment.py`
- `scripts/zigux/check-phase13-landlock-ruleset-packet.py`
- `scripts/zigux/check-phase13-notifier-priority-signal.py`

Keep those missing validator-first helper and route surfaces framed as repo-reality gaps instead of presenting them as a stable shared Phase 13 release handle. `zigux/Makefile` itself is present on current `master`, but it still does not expose the Phase 13 route family, so keep the returned file distinct from the still-missing `phase13` handles.

Current `master` no longer shows that earlier shared-surface drift across `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, or `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`: fresh direct rereads keep the now-returned `Documentation/zigux/phase13-devres-survey.md` and `zigux/tests/phase13_devres_dma_coherent.zig` packet explicit while keeping the still-missing Landlock syscall survey and replay companions in the repo-reality-gap bucket. Any remaining broader release-note follow-through should therefore start with a docs-root reread instead of replaying those already-aligned shared reminder surfaces.

Keep only any still-unverified docs-root follow-through framed as open survey drift until a same-lane reread resolves it or the missing direct `devres` and Landlock syscall packet members actually rematerialize.

Keep older or still-missing direct companions explicit too instead of promoting them into shipped current-`master` evidence when they are not freshly reread in the same run.

## Release-Surface Posture

Keep Phase 13 release wording inside these boundaries:

- the Phase 13 packet is active and roadmap-backed, not closed
- the shared packet is helper-local and reminder-surface backed rather than validator-first in the current direct-readback posture
- the release-note packet should keep any remaining docs-root follow-through explicit while the missing direct Landlock syscall companions stay recorded as repo-reality gaps
- the shared release handle is the materialized docs-root, scripts-root, and tests-root reminder packet listed above together with the shipped shared-summary guard
- the missing validator-first helpers and shared build route surfaces stay explicit as repo-reality gaps
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
- `scripts/zigux/check-phase13-shared-summary-surfaces.py`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

Only widen beyond this survey if a fresh current-`master` reread shows that one of those coupled reminder surfaces cannot stay truthful without the adjacent same-lane follow-through.

## Non-Goals

- This note does not claim a stable validator-first handle on current `master`.
- This note does not claim shipped helper-local parity beyond the directly reread packet.
- This note does not widen into notifier implementation, checker repair, or helper-local tranche closure.
