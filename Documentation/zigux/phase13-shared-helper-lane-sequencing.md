# Phase 13 Shared Helper Lane Sequencing

This note keeps the active Phase 13 shared-subsystems packet split into bounded owner lanes so contributor-facing guidance does not collapse `libfs`, `devres`, `landlock`, and adjacent notifier evidence into one noisy bucket.

## Scope

Use this note when a Phase 13 change touches any part of the shipped shared-helper release packet:

- `fs/libfs.c`
- `lib/devres.c`
- `security/landlock/ruleset.c`
- `security/landlock/syscalls.c`

Adjacent notifier evidence stays in scope for release-surface truthfulness, but it remains adjacent evidence rather than a fifth shared-helper anchor.

## Owner Split

Keep the current owner map explicit:

- `libfs` still owns the roadmap-backed `fs/libfs.c` anchor, but current `master` does not materialize `Documentation/zigux/phase13-libfs-survey.md`, `fs/libfs.zig`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, or `zigux/tests/phase13_libfs_manifest.json`, so keep that starter, reviewability, and manifest packet recorded as repo-reality gaps together with `Documentation/zigux/phase13-libfs-slice.md` and `zigux/tests/phase13_libfs_addressability.zig`
- `devres` owns the currently readable DMA-boundary, planner, survey, and scatterlist helper packet through `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `scripts/zigux/check-phase13-devres-dma-boundary.py`, `scripts/zigux/check-phase13-devres-mmio-packet.py`, `lib/devres.zig`, `lib/devres_scatterlist.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `zigux/tests/phase13_devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist_build.zig`, while `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_manifest.json`, `scripts/zigux/check-phase13-devres-packet.py`, and `scripts/zigux/check-phase13-devres-packet-alignment.py` stay recorded as repo-reality gaps on current `master`
- `landlock/ruleset` owns the ruleset ownership, slice, survey, and focused manifest-backed replay
- `landlock/syscalls` owns the syscall governance, slice, and helper starter surface through `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, and `security/landlock/syscalls.zig`, while `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, the shared `zigux/tests/phase13_build.zig` route, and the live credential, file-descriptor-installation, and ruleset-state surfaces stay recorded as repo-reality gaps on current `master`
- adjacent notifier evidence owns only release-surface truthfulness through `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h`, not a fifth helper family

## Shared Packet Surfaces

Keep these shared reminder surfaces aligned when broad Phase 13 wording changes:

- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `Documentation/zigux/phase13-shared-summary-guard-gap.md`
- `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`
- `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`

shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`

tests-root alignment companion: `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`

do not treat `zigux/Makefile`, `make -C zigux phase13-validate`, or `make -C zigux phase13` as shipped evidence

## Sequencing Rules

1. Prefer one helper lane at a time instead of batching `libfs`, `devres`, `landlock`, and notifier evidence into one mixed change.
2. Treat adjacent notifier evidence as release-surface support, not as an extra shared replay step.
3. Use the shared-summary guard and the tests-root alignment companion before widening contributor wording across the packet.
4. Keep the Makefile-backed route family recorded as repo-reality gaps until current `master` rematerializes the shared build handle.
5. Leave broader docs-root, scripts-root, and tests-root refresh for a separate same-lane follow-up.

## Non-Goals

This note does not widen Phase 13 into:

- a direct filesystem parity claim beyond the roadmap-owned `libfs` anchor while its starter, reviewability, and manifest packet remain repo-reality gaps on current `master`
- a separate shared replay step for notifier evidence
- broader security policy ownership outside the landed Landlock notes
- a claim that the Phase 13 packet is closed or frozen
