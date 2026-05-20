# Phase 13 Roadmap Traceability

This note keeps the roadmap-to-repo owner map truthful for the active Phase 13 shared-helper packet on current `master`.

It is a traceability document only. It does not create a new helper lane, a new replay route, or a tranche-closure claim.

## Roadmap Fit

Phase 13 in the Zigux roadmap is the shared-subsystem-helper tranche.

The roadmap keeps that tranche bounded to four Linux anchors:

- `fs/libfs.c`
- `lib/devres.c`
- `security/landlock/ruleset.c`
- `security/landlock/syscalls.c`

The shared reminder packet should stay tied back to those four anchors instead of collapsing them into one generic Phase 13 bucket or promoting adjacent notifier evidence into a fifth helper family.

## Shared Reminder Surfaces

When shared Phase 13 wording changes, keep these current reminder surfaces aligned first:

- `Documentation/zigux/README.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `scripts/zigux/check-phase13-shared-summary-surfaces.py`
- `scripts/zigux/check-phase13-tests-readme-alignment.py`
- `scripts/zigux/validate-phase13-release.py`
- `zigux/tests/phase13_build.zig`

Keep `zigux/Makefile` distinct from the still-missing shared wrapper names `make -C zigux phase13-validate` and `make -C zigux phase13`. The returned file is current repo evidence again, but those route names still are not the stable shared Phase 13 handle.

## Traceability Snapshot

Use this compact reread before editing the broader Phase 13 packet.

- refresh basis: current `master` direct readback on `2026-05-20`
- roadmap source: `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`
- shared summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`
- shared tests-root alignment guard: `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`
- shared release-discipline validator: `python3 scripts/zigux/validate-phase13-release.py`
- current shared build handle: surrounding reminder surfaces still reference `zigux/tests/phase13_build.zig`, but the current live devres evidence remains narrower and should not be described as if the older direct `phase13-devres`, `phase13-devres-reviewability`, or `phase13-devres-boundary-evidence` companions have returned on current `master`

Current `master` maps the four roadmap anchors to these bounded packet states:

- `fs/libfs.c`: mapped through `Documentation/zigux/phase13-libfs-slice.md`, `Documentation/zigux/phase13-libfs-survey.md`, `fs/libfs.zig`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, `zigux/tests/phase13_libfs_manifest.json`, and the shared `zigux/tests/phase13_build.zig` replay shard while the helper stays bounded below live VFS mutation and deeper filesystem ownership.
- `lib/devres.c`: mapped through `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `lib/devres.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `Documentation/zigux/phase13-devres-scatterlist-slice.md`, `Documentation/zigux/phase13-devres-scatterlist-planner.md`, `lib/devres_scatterlist.zig`, `zigux/tests/phase13_devres_scatterlist.zig`, `zigux/tests/phase13_devres_scatterlist_planner_manifest.json`, `scripts/zigux/check-phase13-devres-dma-boundary.py`, and the historically named `scripts/zigux/check-phase13-devres-mmio-packet.py`, while `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_manifest.json`, and the older direct-helper packet wording remain repo-reality gaps on current `master`.
- `security/landlock/ruleset.c`: mapped through `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `security/landlock/ruleset.zig`, `zigux/tests/phase13_landlock_ruleset.zig`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, and the shared `zigux/tests/phase13_build.zig` replay shard while live tree and hierarchy ownership remain explicitly blocked.
- `security/landlock/syscalls.c`: mapped through `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `security/landlock/syscalls.zig`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, and the shared `zigux/tests/phase13_build.zig` replay shard while live file-descriptor installation, credential replacement, ruleset-state ownership, and full syscall enforcement remain explicitly out of scope.

## Anchor Map

Keep the roadmap-owned helper packet explicit through these bounded owner surfaces:

- `libfs` stays helper-first and reviewable through its slice note, survey note, helper source, direct replay, reviewability replay, manifest, and shared build shard.
- `devres` stays mapped through the current survey-side reminder packet plus the helper-first DMA and scatterlist planner companions, not through a rematerialized direct helper packet. Keep the live owner story anchored to `Documentation/zigux/phase13-devres-survey.md`, the DMA-coherent replay, the planner manifests, the scatterlist planner surfaces, and their checker companions, and keep older continuity lane labels out of this note unless current `master` actually rematerializes the direct `phase13_devres` companions.
- `landlock/ruleset` stays mapped through the ownership note, survey note, helper source, direct replay, manifest, dedicated checker, and shared build shard while keeping live tree and hierarchy state out of scope.
- `landlock/syscalls` stays mapped through the governance note, slice note, survey note, helper source, direct replay, reviewability replay, manifest, and shared build shard while keeping the helper-owned wording tightly scoped to planning and wrapper discipline instead of live syscall enforcement.

## Adjacent Notifier Evidence

Adjacent notifier evidence supports release-surface truthfulness for the same Phase 13 packet, but it does not become a fifth roadmap anchor.

Current `master` now materializes the adjacent notifier packet through:

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

Keep that notifier family explicit as adjacent evidence only. It helps the release-facing packet stay truthful, but it is not a new roadmap-owned helper anchor.

## Repo-Reality Gaps

Keep the remaining current gaps explicit, but do not leave stale missing-file inventories in this note after the files have returned on `master`.

The active shared reminder gaps are now narrower:

- `make -C zigux phase13-validate`
- `make -C zigux phase13`
- `zigux/tests/phase13_devres.zig`
- `zigux/tests/phase13_devres_reviewability.zig`
- `zigux/tests/phase13_devres_boundary_evidence.zig`
- `zigux/tests/phase13_devres_manifest.json`
- live `libfs` filesystem mutation and deeper VFS ownership
- live `devres` DMA, MMIO, scatterlist, and device-tree ownership
- live `landlock/ruleset` tree and hierarchy state
- live `landlock/syscalls` file-descriptor installation, credential replacement, ruleset-state ownership, and full syscall enforcement

Treat those as the bounded current gaps. Do not keep the helper-first DMA and scatterlist planner packet, the Landlock syscall companions, or the notifier-chain helper family in the missing bucket when current `master` materializes them again.

## Boundaries

- This note keeps the roadmap-to-repo map truthful for the active Phase 13 packet.
- This note does not widen Phase 13 into deeper subsystem implementation work.
- This note does not promote notifier evidence into a fifth helper anchor.
- This note does not treat the blocked `make -C zigux phase13-validate` or `make -C zigux phase13` names as the stable shared handle.
- This note does not claim the Phase 13 tranche is closed.
