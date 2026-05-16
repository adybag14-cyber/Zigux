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
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `zigux/tests/README.md`

Those files now show that the shared Phase 13 packet is active, helper-backed, still not closed, and already coupled to the shipped cross-phase contributor-sync and tests-root reminder companions rather than documentation-only.

The coupled current-`master` packet also now keeps the shipped helper-local `libfs`, `devres`, and Landlock notes plus adjacent notifier evidence tied to a validator-first release handle instead of the older "survey-only, scripts-root missing" story.

The helper-local `devres` release wording should stay anchored to `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `zigux/tests/phase13_devres_manifest.json`, and `scripts/zigux/check-phase13-devres-packet-alignment.py`. Those current-`master` companions keep the adjacent coherent-DMA evidence shard and the helper-only DMA/scatterlist boundary explicit without presenting live DMA mappings or live scatterlist ownership as shipped helper parity.

## Current Shared Release Handle

The coupled current-`master` packet now keeps these release surfaces explicit rather than treating them as repo-reality gaps:

- `scripts/zigux/README.md`
- `scripts/zigux/validate-phase13-release.py`
- `zigux/Makefile`
- stable `make -C zigux phase13-validate`
- blocked convenience route `make -C zigux phase13`

Shared release wording should stay anchored to that validator-first handle while `make -C zigux phase13` remains blocked convenience wiring and `zigux/tests/phase13_build.zig` stays a current shared companion surface rather than the stable release handle.

## Repo-Reality Gaps

Keep the remaining shared-summary gap explicit:

- `scripts/zigux/check-phase13-shared-summary-surfaces.py`

Keep older or still-missing direct companions explicit too instead of promoting them into shipped current-`master` evidence:

- `Documentation/zigux/phase13-libfs-slice.md`
- `zigux/tests/phase13_libfs_addressability.zig`
- `scripts/zigux/check-phase13-devres-packet.py`
- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `scripts/zigux/check-phase13-notifier-packet.py`
- `include/zigux/notifier_abi.h`
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`

## Release-Surface Posture

Keep Phase 13 release wording inside these boundaries:

- the Phase 13 packet is active and roadmap-backed, not closed
- the shared packet is helper-local, validator-first, and reminder-surface backed rather than documentation-only
- the stable release handle is `validate-phase13-release.py` plus stable `make -C zigux phase13-validate`
- the broader `make -C zigux phase13` route stays blocked convenience wiring while `zigux/tests/phase13_build.zig` stays a current shared companion surface rather than the stable release handle
- only `scripts/zigux/check-phase13-shared-summary-surfaces.py` stays framed as the remaining shared-summary repo-reality gap
- older helper-local or notifier companions that current `master` still does not materialize stay recorded as repo-reality gaps
- adjacent notifier evidence may still matter for release truthfulness, but it does not become a fifth roadmap anchor
- contributor-facing reminder edits in this lane should stay narrow and should not reopen helper implementation, validator code, or checklist coupling

## Re-Read Before Updating This Note Again

When this survey changes, reread these shared reminder surfaces together first:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

Only widen beyond this survey if a fresh current-`master` reread shows that one of those coupled reminder surfaces cannot stay truthful without the adjacent same-lane follow-through.

## Non-Goals

- This note does not claim a stable shared replay route beyond the validator-first handle.
- This note does not claim shipped helper-local parity beyond the directly coupled current packet.
- This note does not widen into notifier implementation, release-validator repair, or helper-local tranche closure.