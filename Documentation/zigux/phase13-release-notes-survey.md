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
- `Documentation/zigux/phase12-phase13-release-handoff.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-release-packet-index.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-shared-summary-guard-gap.md`
- `Documentation/zigux/phase13-notifier-summary-gap.md`
- `scripts/zigux/check-phase13-tests-readme-alignment.py`
- `scripts/zigux/check-phase13-shared-summary-surfaces.py`
- `scripts/zigux/README.md`
- `scripts/zigux/validate-phase13-release.py`
- `zigux/tests/README.md`

Those files keep the shared Phase 13 packet active and still not closed. Current `master` now also keeps the old missing-checker gap closed through `Documentation/zigux/phase13-shared-summary-guard-gap.md` and `scripts/zigux/check-phase13-shared-summary-surfaces.py`, and the broader docs-root `devres` reminder repair remains landed as a separate same-lane follow-through rather than an open shared-summary gap.

Direct current-`master` rereads in this run show that this survey keeps the release-facing `devres` packet narrowed to `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `scripts/zigux/check-phase13-devres-dmam-alloc-coherent-planner.py`, `Documentation/zigux/phase13-devres-iounmap-planner.md`, `Documentation/zigux/phase13-devres-iomap-planner.md`, `Documentation/zigux/phase13-devres-scatterlist-slice.md`, `Documentation/zigux/phase13-devres-scatterlist-planner.md`, `scripts/zigux/check-phase13-devres-dma-boundary.py`, `scripts/zigux/check-phase13-devres-iounmap-planner.py`, `scripts/zigux/check-phase13-devres-iomap-planner.py`, `scripts/zigux/check-phase13-devres-mmio-packet.py`, `scripts/zigux/check-phase13-devres-current-packet.py`, `scripts/zigux/check-phase13-devres-scatterlist-planner.py`, `lib/devres.zig`, `lib/devres_scatterlist.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `zigux/tests/phase13_devres_dmam_alloc_zero_size_replay_build.zig`, `zigux/tests/phase13_devres_iounmap_planner.zig`, `zigux/tests/phase13_devres_iounmap_planner_manifest.json`, `zigux/tests/phase13_devres_iomap_planner.zig`, `zigux/tests/phase13_devres_iomap_planner_manifest.json`, `zigux/tests/phase13_devres_scatterlist.zig`, `zigux/tests/phase13_devres_scatterlist_build.zig`, and `zigux/tests/phase13_devres_scatterlist_planner_manifest.json`.

Fresh direct readback now shows the broader reminder packet is no longer split across the shared reminder surfaces. `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, `Documentation/zigux/phase13-release-packet-index.md`, `Documentation/zigux/phase13-release-coordination-matrix.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` now all mirror the wider planner-expanded `devres` packet, including the dedicated `dmam_alloc_coherent()` planner checker, the dedicated current-packet checker, and the helper-first `devm_iounmap()` and `devm_of_iomap()` planner note-and-manifest pairings. Current `master` now also materializes the direct `landlock/syscalls` replay pair through `zigux/tests/phase13_landlock_syscalls.zig` and `zigux/tests/phase13_landlock_syscalls_reviewability.zig`. Keep `zigux/tests/phase13_landlock_syscalls_manifest.json` recorded as the remaining direct repo-reality gap instead of promoting the helper-local packet into a closed shared build handle. Current `master` now materializes `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-survey-gap.md`, and `scripts/zigux/check-phase13-landlock-syscalls-packet.py`, so keep that helper-local survey, breadcrumb, checker, and shipped replay pair explicit beside the still-missing direct manifest companion.

Current `master` also now materializes `scripts/zigux/validate-phase13-release.py`, so keep that shared release-discipline validator explicit beside the shipped shared-summary guard, the stable contributor-facing handle, and the compact packet index while the remaining same-lane follow-through stays narrowed to still-missing direct companions or any future broader reminder drift.

Current `master` also keeps the helper-local packet split visible from the release surface:

- `libfs` stays roadmap-owned, and current `master` now materializes the helper-first slice, survey, and tests-root packet through `Documentation/zigux/phase13-libfs-slice.md`, `Documentation/zigux/phase13-libfs-survey.md`, `fs/libfs.zig`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, and `zigux/tests/phase13_libfs_manifest.json`, while `zigux/tests/phase13_libfs_addressability.zig` remains a separate repo-reality gap and `zigux/tests/phase13_build.zig` still remains absent on current `master`
- `devres` stays anchored through `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `scripts/zigux/check-phase13-devres-dma-boundary.py`, `scripts/zigux/check-phase13-devres-mmio-packet.py`, `scripts/zigux/check-phase13-devres-current-packet.py`, `scripts/zigux/check-phase13-devres-scatterlist-planner.py`, `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `scripts/zigux/check-phase13-devres-dmam-alloc-coherent-planner.py`, `Documentation/zigux/phase13-devres-iounmap-planner.md`, `Documentation/zigux/phase13-devres-iomap-planner.md`, `Documentation/zigux/phase13-devres-scatterlist-slice.md`, `Documentation/zigux/phase13-devres-scatterlist-planner.md`, `scripts/zigux/check-phase13-devres-iounmap-planner.py`, `scripts/zigux/check-phase13-devres-iomap-planner.py`, `lib/devres.zig`, `lib/devres_scatterlist.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `zigux/tests/phase13_devres_dmam_alloc_zero_size_replay_build.zig`, `zigux/tests/phase13_devres_iounmap_planner.zig`, `zigux/tests/phase13_devres_iounmap_planner_manifest.json`, `zigux/tests/phase13_devres_iomap_planner.zig`, `zigux/tests/phase13_devres_iomap_planner_manifest.json`, `zigux/tests/phase13_devres_scatterlist.zig`, `zigux/tests/phase13_devres_scatterlist_build.zig`, and `zigux/tests/phase13_devres_scatterlist_planner_manifest.json`, while older `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_manifest.json`, `scripts/zigux/check-phase13-devres-packet.py`, and `scripts/zigux/check-phase13-devres-packet-alignment.py` stay explicit repo-reality gaps
- `landlock/ruleset` stays helper-local through its ownership note, survey, source, manifest-backed replay surfaces, and dedicated packet checker, while the direct `Documentation/zigux/phase13-landlock-ruleset-slice.md` note and the shared `zigux/tests/phase13_build.zig` route still remain repo-reality gaps; `landlock/syscalls` stays helper-local through its governance note, slice, survey, historical `Documentation/zigux/phase13-landlock-syscalls-survey-gap.md` breadcrumb, packet checker, and source starter without collapsing into docs-only governance metadata, the direct syscall replay and reviewability companions stay explicit as shipped current-`master` evidence, and the direct syscall manifest companion still stays recorded as a repo-reality gap
- adjacent notifier evidence remains support material rather than a fifth roadmap anchor, while the still-missing `zigux/helpers/notifier_chain_view.zig`, `include/zigux/notifier_abi.h`, and `scripts/zigux/check-phase13-notifier-priority-signal.py` remain separate repo-reality gaps rather than release-facing proof

## Current Shared Release Handle

The release-planning handle that is directly supportable from this run stays anchored to the materialized reminder surfaces and their active shared companions:

- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-release-packet-index.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase12-phase13-release-handoff.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-shared-summary-guard-gap.md`
- `Documentation/zigux/phase13-notifier-summary-gap.md`
- `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`
- `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`
- `python3 scripts/zigux/validate-phase13-release.py`

Keep broad release wording tied to that reminder packet while the missing validator-first helpers, adjacent notifier companions, and route surfaces remain explicit repo-reality gaps.

## Repo-Reality Gaps

Direct current-`master` readback in this run still returned missing for:

- `zigux/tests/phase13_libfs_addressability.zig`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`
- `zigux/tests/phase13_build.zig`
- `scripts/zigux/check-phase13-devres-packet.py`
- `scripts/zigux/check-phase13-devres-packet-alignment.py`
- `Documentation/zigux/phase13-landlock-ruleset-slice.md`
- `zigux/tests/phase13_landlock_syscalls_manifest.json`
- `scripts/zigux/check-phase13-notifier-priority-signal.py`
- `zigux/helpers/notifier_chain_view.zig`
- `include/zigux/notifier_abi.h`

Keep those missing validator-first helper, adjacent notifier companion, and route surfaces framed as repo-reality gaps instead of presenting them as a stable shared Phase 13 release handle. `zigux/Makefile` itself is present on current `master`, but it still does not expose the Phase 13 route family, so keep the returned file distinct from the still-missing `phase13` handles. Current `master` now also materializes `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-survey-gap.md`, and `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, so keep the returned Landlock ruleset ownership note, survey, syscall breadcrumb, and checker surfaces explicit beside the still-missing direct ruleset slice note plus the remaining direct syscall manifest companion rather than listing those returned helper-local surfaces as release-facing gaps.

Current `master` now keeps `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, `Documentation/zigux/phase13-release-packet-index.md`, `Documentation/zigux/phase13-release-coordination-matrix.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` aligned on the wider planner-expanded `devres` packet. At the same time, the shared reminder packet now keeps both the shipped helper-first `libfs` slice and the returned `Documentation/zigux/phase13-libfs-survey.md` explicit, keeps `zigux/tests/phase13_libfs_addressability.zig` recorded as a repo-reality gap, and keeps `scripts/zigux/validate-phase13-release.py` explicit as shipped release-discipline support. `Documentation/zigux/phase13-notifier-summary-gap.md` keeps the missing notifier-chain helper and notifier header recorded beside the shipped adjacent notifier evidence, so the remaining follow-through now stays limited to those still-missing direct companions or any future broader reminder drift instead of the older scripts-root repair or the now-closed tests-root validator-gap story.

Keep older or still-missing direct companions explicit too instead of promoting them into shipped current-`master` evidence when they are not freshly reread in the same run.

## Release-Surface Posture

Keep Phase 13 release wording inside these boundaries:

- the Phase 13 packet is active and roadmap-backed, not closed
- the shared packet is helper-local and reminder-surface backed rather than validator-first in the current direct-readback posture
- the release-note packet should keep the already-landed docs-root repair intact while the remaining direct Landlock syscall manifest companion stays recorded as a repo-reality gap
- the shared release handle is the materialized docs-root, scripts-root, and tests-root reminder packet listed above together with the shipped shared-summary guard and the compact packet index
- the missing validator-first helpers, adjacent notifier-chain helper, adjacent notifier header, and shared build route surfaces stay explicit as repo-reality gaps
- adjacent notifier evidence may still matter for release truthfulness, but it does not become a fifth roadmap anchor
- contributor-facing reminder edits in this lane should stay narrow and should not reopen helper implementation, checker code, or tranche-closure claims

## Re-Read Before Updating This Note Again

When this survey changes, reread these shared reminder surfaces together first:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-release-packet-index.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-shared-summary-guard-gap.md`
- `Documentation/zigux/phase13-notifier-summary-gap.md`
- `Documentation/zigux/phase12-phase13-release-handoff.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `scripts/zigux/check-phase13-tests-readme-alignment.py`
- `scripts/zigux/check-phase13-shared-summary-surfaces.py`
- `scripts/zigux/validate-phase13-release.py`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

If the release-facing `devres` packet is what moved, reread these same-lane packet surfaces in the same pass before changing this note:

- `Documentation/zigux/phase13-devres-slice.md`
- `Documentation/zigux/phase13-devres-survey.md`
- `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`
- `scripts/zigux/check-phase13-devres-dmam-alloc-coherent-planner.py`
- `Documentation/zigux/phase13-devres-iounmap-planner.md`
- `Documentation/zigux/phase13-devres-iomap-planner.md`
- `Documentation/zigux/phase13-devres-scatterlist-slice.md`
- `Documentation/zigux/phase13-devres-scatterlist-planner.md`
- `scripts/zigux/check-phase13-devres-dma-boundary.py`
- `scripts/zigux/check-phase13-devres-iounmap-planner.py`
- `scripts/zigux/check-phase13-devres-iomap-planner.py`
- `scripts/zigux/check-phase13-devres-mmio-packet.py`
- `scripts/zigux/check-phase13-devres-current-packet.py`
- `scripts/zigux/check-phase13-devres-scatterlist-planner.py`
- `lib/devres.zig`
- `lib/devres_scatterlist.zig`
- `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`
- `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`
- `zigux/tests/phase13_devres_dmam_alloc_zero_size_replay_build.zig`
- `zigux/tests/phase13_devres_dma_coherent.zig`
- `zigux/tests/phase13_devres_iounmap_planner.zig`
- `zigux/tests/phase13_devres_iounmap_planner_manifest.json`
- `zigux/tests/phase13_devres_iomap_planner.zig`
- `zigux/tests/phase13_devres_iomap_planner_manifest.json`
- `zigux/tests/phase13_devres_scatterlist.zig`
- `zigux/tests/phase13_devres_scatterlist_build.zig`
- `zigux/tests/phase13_devres_scatterlist_planner_manifest.json`

Only widen beyond this survey if a fresh current-`master` reread shows that one of those coupled reminder surfaces cannot stay truthful without the adjacent same-lane follow-through.

## Non-Goals

- This note does not claim a stable validator-first handle on current `master`.
- This note does not claim shipped helper-local parity beyond the directly reread packet.
- This note does not widen into notifier implementation, checker repair, or helper-local tranche closure.