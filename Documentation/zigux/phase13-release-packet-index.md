# Phase 13 Release Packet Index

This note is the compact PMO packet index for the active Phase 13 shared-helper release packet.

It exists to keep the shared release packet easy to reread from one place without widening release claims, closing the tranche, or inventing a shared build route that current `master` still does not expose.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_RELEASE_CLOSED=no`
- lane owner: `pmo-release`
- scope: phase sequencing, tranche-closure tracking, and release-note coordination for the active Phase 13 shared-helper packet on current `master`
- authority model: repo-first current-`master` readback, with the roadmap and ledger used only to keep the packet bounded to the four shared-helper anchors

## Shared PMO Packet

### Docs-root packet

The shared release-planning packet is currently anchored by:

- `Documentation/zigux/phase13-release-packet-index.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase12-phase13-release-handoff.md`
- `Documentation/zigux/phase13-shared-summary-guard-gap.md`
- `Documentation/zigux/phase13-notifier-summary-gap.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`

### Scripts-root support bundle

The directly readable release-discipline bundle is currently:

- `scripts/zigux/check-phase13-shared-summary-surfaces.py`
- `scripts/zigux/check-phase13-tests-readme-alignment.py`
- `scripts/zigux/check-phase13-roadmap-traceability.py`
- `scripts/zigux/validate-phase13-release.py`
- `scripts/zigux/README.md`

### Tests-root reminder packet

The shared reminder packet is currently anchored by:

- `zigux/tests/README.md`

No shared Phase 13 build handle is returned on current `master`. Keep `make -C zigux phase13-validate`, `make -C zigux phase13`, and `zigux/tests/phase13_build.zig` explicit as repo-reality gaps rather than shared packet evidence.

## Helper-Local Split

Keep the shared packet tied to the four roadmap-owned anchors without collapsing their helper-local evidence into a fake closed tranche:

- `libfs` stays helper-first through `Documentation/zigux/phase13-libfs-slice.md`, `Documentation/zigux/phase13-libfs-survey.md`, `fs/libfs.zig`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, and `zigux/tests/phase13_libfs_manifest.json`, while `zigux/tests/phase13_libfs_addressability.zig` and `zigux/tests/phase13_build.zig` stay repo-reality gaps
- `devres` stays release-visible through `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `Documentation/zigux/phase13-devres-iomap-planner.md`, `Documentation/zigux/phase13-devres-iounmap-planner.md`, `Documentation/zigux/phase13-devres-scatterlist-slice.md`, `Documentation/zigux/phase13-devres-scatterlist-planner.md`, `scripts/zigux/check-phase13-devres-dma-boundary.py`, `scripts/zigux/check-phase13-devres-dmam-alloc-coherent-planner.py`, `scripts/zigux/check-phase13-devres-iomap-planner.py`, `scripts/zigux/check-phase13-devres-iounmap-planner.py`, `scripts/zigux/check-phase13-devres-mmio-packet.py`, `scripts/zigux/check-phase13-devres-current-packet.py`, `scripts/zigux/check-phase13-devres-scatterlist-planner.py`, `lib/devres.zig`, `lib/devres_scatterlist.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `zigux/tests/phase13_devres_dmam_alloc_zero_size_replay_build.zig`, `zigux/tests/phase13_devres_iomap_planner.zig`, `zigux/tests/phase13_devres_iomap_planner_manifest.json`, `zigux/tests/phase13_devres_iounmap_planner.zig`, `zigux/tests/phase13_devres_iounmap_planner_manifest.json`, `zigux/tests/phase13_devres_scatterlist.zig`, `zigux/tests/phase13_devres_scatterlist_build.zig`, and `zigux/tests/phase13_devres_scatterlist_planner_manifest.json`
- `landlock/ruleset` stays helper-local through `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `security/landlock/ruleset.zig`, `zigux/tests/phase13_landlock_ruleset.zig`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, and `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, while `Documentation/zigux/phase13-landlock-ruleset-slice.md` and the shared `zigux/tests/phase13_build.zig` route stay repo-reality gaps
- `landlock/syscalls` stays helper-local through `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-survey-gap.md`, `scripts/zigux/check-phase13-landlock-syscalls-packet.py`, `security/landlock/syscalls.zig`, `zigux/tests/phase13_landlock_syscalls.zig`, and `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, while `zigux/tests/phase13_landlock_syscalls_manifest.json` stays a repo-reality gap
- adjacent notifier evidence stays support-only through `Documentation/zigux/phase13-notifier-list-survey.md`, `Documentation/zigux/phase13-notifier-summary-gap.md`, `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h` without becoming a fifth roadmap anchor

## Repo-Reality Gaps

Keep these surfaces explicit as gaps instead of release-facing proof:

- `make -C zigux phase13-validate`
- `make -C zigux phase13`
- `zigux/tests/phase13_build.zig`
- `zigux/tests/phase13_libfs_addressability.zig`
- `Documentation/zigux/phase13-landlock-ruleset-slice.md`
- `zigux/tests/phase13_landlock_syscalls_manifest.json`
- `scripts/zigux/check-phase13-notifier-priority-signal.py`
- `zigux/helpers/notifier_chain_view.zig`
- `include/zigux/notifier_abi.h`

## Release Boundaries

- This index is a coordination artifact, not a closure claim.
- This index does not imply a shipped shared Makefile route for Phase 13.
- This index does not promote adjacent notifier evidence into a fifth helper anchor.
- This index does not widen into helper implementation, checker repair, or Phase 14 study-only territory.

## Next Bounded PMO Step

Leave this index parked unless one of the shared release companions drifts again.

If that happens, reread this index beside `Documentation/zigux/phase13-release-coordination-matrix.md`, `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/phase12-phase13-release-handoff.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`, then land only the smallest reminder-side truthfulness repair and rerun `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`, `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`, `python3 scripts/zigux/check-phase13-roadmap-traceability.py`, and `python3 scripts/zigux/validate-phase13-release.py`.