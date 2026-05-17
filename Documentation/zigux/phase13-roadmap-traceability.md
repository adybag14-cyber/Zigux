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

The surrounding shared-summary packet should stay tied back to those four anchors instead of drifting into a generic reminder surface or treating adjacent notifier evidence as a fifth helper lane.

## Shared Packet Surfaces

When shared Phase 13 wording changes, keep these current shared surfaces aligned:

- `Documentation/zigux/README.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-shared-summary-guard-gap.md`
- `Documentation/zigux/phase13-notifier-summary-gap.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/check-phase13-tests-readme-alignment.py`
- `scripts/zigux/check-phase13-shared-summary-surfaces.py`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

Keep the broader docs-root, scripts-root, tests-root, shared-summary-gap, and notifier-gap packet explicit as the current reminder surface, and keep the older Makefile-backed handle explicit as repo-reality-gap vocabulary instead of a materialized shared surface while current `master` still does not materialize `zigux/Makefile`, `make -C zigux phase13-validate`, or blocked convenience route `make -C zigux phase13`.

## Anchor Map

Keep the roadmap-owned helper packet explicit through these bounded owner surfaces:

- `libfs` stays mapped through `Documentation/zigux/phase13-libfs-survey.md`, the shipped `fs/libfs.zig` starter, the direct `zigux/tests/phase13_libfs.zig` replay, the direct `zigux/tests/phase13_libfs_reviewability.zig` companion, and `zigux/tests/phase13_libfs_manifest.json`.
- `devres` stays mapped through `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, the shipped `lib/devres.zig` starter, the direct `zigux/tests/phase13_devres.zig` replay, the direct `zigux/tests/phase13_devres_reviewability.zig` companion, `zigux/tests/phase13_devres_manifest.json`, the shipped DMA-boundary checker pair `scripts/zigux/check-phase13-devres-dma-boundary.py` and `scripts/zigux/check-phase13-devres-mmio-packet.py`, and `zigux/tests/phase13_devres_dma_coherent.zig`. The planning-only `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `Documentation/zigux/phase13-devres-scatterlist-slice.md`, `lib/devres_scatterlist.zig`, `zigux/tests/phase13_devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist_build.zig` stay adjacent boundary evidence rather than proof of live DMA or scatterlist parity. Older `zigux/tests/phase13_devres_boundary_evidence.zig` and `scripts/zigux/check-phase13-devres-packet.py` should stay framed as stale or missing companion history rather than as the current active devres packet. Keep the scheduled owner split anchored to `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`: the repo packet id remains `P13-L01`, while shared-lane follow-through stays split across `P13-L05` packet truthfulness, `P13-L06` bounded helper work, and `P13-L07` verification-only replay so those labels do not drift into competing devres owner stories.
- `landlock/ruleset` stays mapped through `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, the shipped `security/landlock/ruleset.zig` starter, the direct `zigux/tests/phase13_landlock_ruleset.zig` replay, and `zigux/tests/phase13_landlock_ruleset_manifest.json`.
- `landlock/syscalls` stays mapped through `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, and the shipped `security/landlock/syscalls.zig` starter. Keep the helper-owned wording tightly scoped to descriptor-backed create-ruleset planning, ruleset-fd install planning, and ruleset-fd stub discipline planning, and keep `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` framed as repo-reality gaps until current `master` materializes them again so the reminder packet does not overstate the live syscall helper surface.

## Adjacent Evidence

Adjacent notifier evidence supports release-surface truthfulness for the same Phase 13 packet, but it still does not become a fifth roadmap anchor.

Current `master` still does not materialize `Documentation/zigux/phase13-notifier-list-survey.md`, so keep that note framed as a repo-reality gap and keep the surviving adjacent notifier packet explicit through:

- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `zigux/bindings/notifier_abi.zig`
- `zigux/helpers/notifier_chain_view.zig`
- `include/zigux/abi.h`
- `drivers/tty/hvc/hvc_console.h`

Keep `zigux/Makefile`, `make -C zigux phase13-validate`, and blocked convenience route `make -C zigux phase13` framed as repo-reality gaps here too while the missing shared build companion and notifier survey keep the broader make-route handle from qualifying as current adjacent evidence.

## Repo-Reality Gaps

Keep the remaining shared-summary, validator-first, and direct-companion gaps explicit until current `master` materializes them again:

- `zigux/Makefile`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`
- `scripts/zigux/validate-phase13-release.py`
- `scripts/zigux/check-phase13-landlock-ruleset-packet.py`
- `scripts/zigux/check-phase13-notifier-priority-signal.py`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `Documentation/zigux/phase13-libfs-slice.md`
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `zigux/tests/phase13_build.zig`
- `zigux/tests/phase13_libfs_addressability.zig`
- `zigux/tests/phase13_landlock_syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
- `zigux/tests/phase13_landlock_syscalls_manifest.json`
- `scripts/zigux/check-phase13-devres-packet.py`
- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `scripts/zigux/check-phase13-notifier-packet.py`
- `include/zigux/notifier_abi.h`
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`

Current `master` now materializes `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-shared-summary-guard-gap.md`, and `scripts/zigux/check-phase13-shared-summary-surfaces.py` alongside the surviving bounded `devres` coordination packet, so keep those surfaces aligned as shipped shared evidence while the missing validator-first checker packet, the absent notifier survey, the absent shared build companion, the still-missing direct Landlock syscall companions, and the older missing notifier companions stay recorded here as repo-reality gaps. That gap set is also what keeps `make -C zigux phase13` framed as blocked convenience wiring rather than a stable shared replay handle.

## Boundaries

- This note keeps the roadmap-to-repo map truthful for the active Phase 13 packet.
- This note does not widen Phase 13 into deeper subsystem implementation work.
- This note does not promote notifier evidence into a fifth helper anchor.
- This note does not treat blocked `make -C zigux phase13` wiring as the stable shared replay handle.
- This note does not claim the Phase 13 tranche is closed.
