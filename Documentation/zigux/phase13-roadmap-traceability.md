# Phase 13 Roadmap Traceability

This note restores the roadmap-to-repo owner map for the active Phase 13 shared-helper packet on current `master`.

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
- `Documentation/zigux/phase13-shared-summary-guard-gap.md`
- `Documentation/zigux/phase13-notifier-summary-gap.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `scripts/zigux/check-phase13-shared-summary-surfaces.py`
- `scripts/zigux/check-phase13-tests-readme-alignment.py`
- `scripts/zigux/validate-phase13-release.py`

Keep `zigux/Makefile` distinct from the still-missing shared wrapper names `make -C zigux phase13-validate` and `make -C zigux phase13`. The returned file is current repo evidence again, but those route names still are not the stable shared Phase 13 handle.

## Traceability Snapshot

Use this compact reread before editing the broader Phase 13 packet.

- refresh basis: current `master` direct readback on `2026-05-21`
- roadmap source: `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`
- stable shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`
- shared tests-root alignment guard: `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`
- shared release-discipline validator: `python3 scripts/zigux/validate-phase13-release.py`

Keep the broader docs-root, scripts-root, tests-root, shared-summary-gap, and notifier-gap packet explicit as the current reminder surface.

Current `master` now materializes `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-shared-summary-guard-gap.md`, `scripts/zigux/check-phase13-shared-summary-surfaces.py`, `Documentation/zigux/phase13-notifier-list-survey.md`, and the surrounding shared reminder packet, while the Phase 13 Makefile route family still remains missing.

Current `master` now materializes `scripts/zigux/validate-phase13-release.py`, so keep that validator explicit as shipped release-discipline support for the shared Phase 13 reminder packet instead of carrying it with the still-missing validator-first checker packet, absent shared build companion, still-missing direct Landlock syscall companions, older direct devres companions, and missing notifier-chain companion.

## Anchor Map

Current `master` maps the four roadmap anchors to these bounded packet states:

- `fs/libfs.c`: mapped through `Documentation/zigux/phase13-libfs-slice.md`, `fs/libfs.zig`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, and `zigux/tests/phase13_libfs_manifest.json`, while `Documentation/zigux/phase13-libfs-survey.md`, `zigux/tests/phase13_libfs_addressability.zig`, and the shared `zigux/tests/phase13_build.zig` replay route stay recorded as repo-reality gaps on current `master`.
- `lib/devres.c`: `devres` stays mapped through `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, the shipped DMA-boundary checker pair `scripts/zigux/check-phase13-devres-dma-boundary.py` and the historically named `scripts/zigux/check-phase13-devres-mmio-packet.py`, `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `Documentation/zigux/phase13-devres-scatterlist-planner.md`, `Documentation/zigux/phase13-devres-scatterlist-slice.md`, `zigux/tests/phase13_devres_scatterlist_planner_manifest.json`, `lib/devres.zig`, `lib/devres_scatterlist.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist_build.zig`, while `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_manifest.json`, and `scripts/zigux/check-phase13-devres-packet-alignment.py` remain repo-reality gaps on current `master`.
- `security/landlock/ruleset.c`: mapped through `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `security/landlock/ruleset.zig`, `zigux/tests/phase13_landlock_ruleset.zig`, and `zigux/tests/phase13_landlock_ruleset_manifest.json`, while broader tree and hierarchy state remains out of scope.
- `security/landlock/syscalls.c`: mapped through `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, and `security/landlock/syscalls.zig`. Keep the helper-owned wording tightly scoped to descriptor-backed create-ruleset planning, and keep `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` framed as repo-reality gaps until current `master` materializes them again.

## Adjacent Notifier Evidence

Adjacent notifier evidence supports release-surface truthfulness for the same Phase 13 packet, but it does not become a fifth roadmap anchor.

Current `master` now materializes the adjacent notifier packet through:

- `Documentation/zigux/phase13-notifier-list-survey.md`
- `scripts/zigux/check-phase13-notifier-packet.py`
- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `zigux/bindings/notifier_abi.zig`
- `include/zigux/abi.h`
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`
- `drivers/tty/hvc/hvc_console.h`

Keep that notifier family explicit as adjacent evidence only. It helps the release-facing packet stay truthful, but it is not a new roadmap-owned helper anchor.

## Repo-Reality Gaps

Keep the remaining current gaps explicit, but do not leave stale missing-file inventories in this note after the files have returned on `master`.

The active shared reminder gaps are now narrower:

- `make -C zigux phase13-validate`
- `make -C zigux phase13`
- `Documentation/zigux/phase13-libfs-survey.md`
- `zigux/tests/phase13_libfs_addressability.zig`
- `zigux/tests/phase13_build.zig`
- `zigux/tests/phase13_devres.zig`
- `zigux/tests/phase13_devres_reviewability.zig`
- `zigux/tests/phase13_devres_boundary_evidence.zig`
- `zigux/tests/phase13_devres_manifest.json`
- `scripts/zigux/check-phase13-devres-packet-alignment.py`
- `scripts/zigux/check-phase13-landlock-ruleset-packet.py`
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `zigux/tests/phase13_landlock_syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
- `zigux/tests/phase13_landlock_syscalls_manifest.json`
- `zigux/helpers/notifier_chain_view.zig`
- `scripts/zigux/check-phase13-notifier-priority-signal.py`
- `include/zigux/notifier_abi.h`
- live `libfs` filesystem mutation and deeper VFS ownership
- live `devres` DMA, MMIO, scatterlist, and device-tree ownership
- live `landlock/ruleset` tree and hierarchy state
- live `landlock/syscalls` file-descriptor installation, credential replacement, ruleset-state ownership, and full syscall enforcement

Treat those as the bounded current gaps.

## Boundaries

- This note keeps the roadmap-to-repo map truthful for the active Phase 13 packet.
- This note does not widen Phase 13 into deeper subsystem implementation work.
- This note does not promote notifier evidence into a fifth helper anchor.
- This note does not treat the blocked `make -C zigux phase13-validate` or `make -C zigux phase13` names as the stable shared handle.
- This note does not claim the Phase 13 tranche is closed.
