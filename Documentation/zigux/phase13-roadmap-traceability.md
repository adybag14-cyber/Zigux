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

- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `scripts/zigux/validate-phase13-release.py`
- `zigux/Makefile`
- stable `make -C zigux phase13-validate`
- blocked convenience route `make -C zigux phase13`

## Anchor Map

Keep the roadmap-owned helper packet explicit through these bounded owner surfaces:

- `libfs` stays mapped through `Documentation/zigux/phase13-libfs-survey.md`, the shipped `fs/libfs.zig` starter, the direct `zigux/tests/phase13_libfs.zig` replay, the direct `zigux/tests/phase13_libfs_reviewability.zig` companion, and `zigux/tests/phase13_libfs_manifest.json`.
- `devres` stays mapped through `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, the shipped `lib/devres.zig` starter, the direct `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, and `zigux/tests/phase13_devres_boundary_evidence.zig` companions, `zigux/tests/phase13_devres_manifest.json`, and `scripts/zigux/check-phase13-devres-packet-alignment.py`.
- `landlock/ruleset` stays mapped through `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, the shipped `security/landlock/ruleset.zig` starter, the direct `zigux/tests/phase13_landlock_ruleset.zig` replay, `zigux/tests/phase13_landlock_ruleset_manifest.json`, and `scripts/zigux/check-phase13-landlock-ruleset-packet.py`.
- `landlock/syscalls` stays mapped through `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, the shipped `security/landlock/syscalls.zig` starter, the direct `zigux/tests/phase13_landlock_syscalls.zig` replay, the direct `zigux/tests/phase13_landlock_syscalls_reviewability.zig` companion, and `zigux/tests/phase13_landlock_syscalls_manifest.json`.

## Adjacent Evidence

Adjacent notifier evidence supports release-surface truthfulness for the same Phase 13 packet, but it still does not become a fifth roadmap anchor.

Keep that adjacent packet explicit through:

- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `scripts/zigux/check-phase13-notifier-priority-signal.py`
- `scripts/zigux/validate-phase13-release.py`
- `zigux/bindings/notifier_abi.zig`
- `zigux/helpers/notifier_chain_view.zig`
- `include/zigux/abi.h`
- `drivers/tty/hvc/hvc_console.h`
- `zigux/Makefile`
- stable `make -C zigux phase13-validate`
- blocked convenience route `make -C zigux phase13`

## Repo-Reality Gaps

Keep these Phase 13 shared-summary gaps explicit until current `master` materializes them again:

- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `scripts/zigux/check-phase13-shared-summary-surfaces.py`
- `zigux/tests/phase13_build.zig`

Keep older or missing direct helper companions recorded as repo-reality gaps when current `master` cannot materialize them instead of presenting them here as shipped evidence.

## Boundaries

- This note keeps the roadmap-to-repo map truthful for the active Phase 13 packet.
- This note does not widen Phase 13 into deeper subsystem implementation work.
- This note does not promote notifier evidence into a fifth helper anchor.
- This note does not treat blocked `make -C zigux phase13` wiring as the stable shared replay handle.
- This note does not claim the Phase 13 tranche is closed.
