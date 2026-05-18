# Phase 13 Contributor Workflow Guide

Use this guide when a change touches the active Phase 13 shared-helper packet and the review needs one contributor-facing workflow note instead of reconstructing the packet from scattered reminder surfaces.

This guide is a shared workflow companion. It is not a tranche-closure note, not a new replay route, and not a reason to collapse helper-local work into one generic Phase 13 bucket.

## Purpose

Keep broad contributor wording aligned with the active Phase 13 helper packet centered on four roadmap-owned Linux anchors:

- `fs/libfs.c`
- `lib/devres.c`
- `security/landlock/ruleset.c`
- `security/landlock/syscalls.c`

Adjacent notifier evidence still matters for release-surface truthfulness, but it remains adjacent evidence rather than a fifth helper family.

## Stable Contributor-Facing Handle

Keep the contributor-facing shared handle aligned through:

1. `Documentation/zigux/phase13-contributor-workflow-guide.md`
2. `scripts/zigux/README.md`
3. `zigux/tests/README.md`
4. `Documentation/zigux/phase13-release-coordination-matrix.md`
5. `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`

stable shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`
tests-root alignment companion: `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`

Keep `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py` explicit as the shipped shared-summary guard for those reminder surfaces rather than as the contributor-facing handle itself.

Keep `python3 scripts/zigux/check-phase13-tests-readme-alignment.py` explicit as the shipped tests-root alignment companion for that stable handle rather than as a new replay route or a Makefile-backed entrypoint.

`zigux/Makefile` is present on current `master`, but it still does not expose `make -C zigux phase13-validate` or `make -C zigux phase13`, so keep the file itself distinct from those missing Phase 13 route names and keep only the route names recorded as repo-reality gaps until the shared build handle returns.

## Shared Surfaces To Reread Together

When shared Phase 13 wording changes, reread these contributor-facing and support surfaces together:

- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-shared-summary-guard-gap.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `scripts/zigux/check-phase13-shared-summary-surfaces.py`
- `scripts/zigux/check-phase13-tests-readme-alignment.py`

Keep broader docs-root refresh as a separate same-lane follow-up instead of mixing it into helper-local packet work.

## Helper-Local Packets

Keep helper-local ownership explicit instead of flattening the packet into a single generic Phase 13 summary.

### `libfs`

- `Documentation/zigux/phase13-libfs-survey.md`
- `fs/libfs.zig`
- `zigux/tests/phase13_libfs.zig`
- `zigux/tests/phase13_libfs_reviewability.zig`
- `zigux/tests/phase13_libfs_manifest.json`

Keep `Documentation/zigux/phase13-libfs-slice.md`, `zigux/tests/phase13_libfs_addressability.zig`, and `zigux/tests/phase13_build.zig` recorded as repo-reality gaps until they rematerialize on current `master`.

### `devres`

- `Documentation/zigux/phase13-devres-slice.md`
- `Documentation/zigux/phase13-devres-survey.md`
- `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`
- `Documentation/zigux/phase13-devres-scatterlist-slice.md`
- `scripts/zigux/check-phase13-devres-dma-boundary.py`
- `scripts/zigux/check-phase13-devres-mmio-packet.py`
- `zigux/tests/phase13_devres_dma_coherent.zig`
- `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`
- `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`
- `lib/devres_scatterlist.zig`
- `zigux/tests/phase13_devres_scatterlist.zig`
- `zigux/tests/phase13_devres_scatterlist_build.zig`

Keep `lib/devres.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_manifest.json`, `scripts/zigux/check-phase13-devres-packet.py`, and `scripts/zigux/check-phase13-devres-packet-alignment.py` recorded as repo-reality gaps until they rematerialize on current `master`.

### `landlock/ruleset`

- `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
- `Documentation/zigux/phase13-landlock-ruleset-slice.md`
- `Documentation/zigux/phase13-landlock-ruleset-survey.md`
- `security/landlock/ruleset.zig`
- `zigux/tests/phase13_landlock_ruleset.zig`
- `zigux/tests/phase13_landlock_ruleset_manifest.json`

### `landlock/syscalls`

- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- `security/landlock/syscalls.zig`

Keep `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` recorded as repo-reality gaps until they rematerialize on current `master`.

## Adjacent Notifier Evidence

Keep notifier evidence explicit as adjacent release-surface support through:

- `Documentation/zigux/phase13-notifier-list-survey.md`
- `zigux/bindings/notifier_abi.zig`
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`
- `include/zigux/abi.h`
- `drivers/tty/hvc/hvc_console.h`

Keep `zigux/helpers/notifier_chain_view.zig`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, and `include/zigux/notifier_abi.h` recorded as repo-reality gaps until they rematerialize on current `master`. `zigux/Makefile` is present again, but `make -C zigux phase13-validate` and `make -C zigux phase13` still remain repo-reality-gap route names until that Phase 13 shared build handle is restored.

## Reviewer Prompt

Before landing a broad Phase 13 reminder change, check that:

- the contributor-facing handle still runs through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`
- the release-coordination matrix and shared-helper sequencing note still describe the same active helper packet
- the stable shared-summary guard remains `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`
- the shipped tests-root alignment companion remains `python3 scripts/zigux/check-phase13-tests-readme-alignment.py` so the broader contributor wording and the tests-root reminder stay on the same Phase 13 packet
- helper-local owner maps for `libfs`, `devres`, and `landlock` remain explicit
- the shipped `devres` packet still runs through `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `Documentation/zigux/phase13-devres-scatterlist-slice.md`, `scripts/zigux/check-phase13-devres-dma-boundary.py`, `scripts/zigux/check-phase13-devres-mmio-packet.py`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `lib/devres_scatterlist.zig`, `zigux/tests/phase13_devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist_build.zig`, while `lib/devres.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_manifest.json`, `scripts/zigux/check-phase13-devres-packet.py`, and `scripts/zigux/check-phase13-devres-packet-alignment.py` stay recorded as repo-reality gaps rather than shipped current-`master` evidence
- adjacent notifier evidence stays adjacent rather than becoming a fifth helper family
- the returned notifier survey, `zigux/bindings/notifier_abi.zig`, and the `list_view` and `hlist_view` helpers stay explicit as adjacent evidence without being promoted into the shared helper handle
- `zigux/helpers/notifier_chain_view.zig` stays recorded as a repo-reality gap, while `zigux/Makefile` stays distinguished from the still-missing `make -C zigux phase13-validate` and `make -C zigux phase13` route names instead of promoting that partial build surface into shipped current-`master` Phase 13 evidence
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, and `security/landlock/syscalls.zig` stay explicit as the current Landlock syscall starter surfaces while `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` stay recorded as repo-reality gaps rather than shipped current-`master` evidence

## Non-Goals

This guide does not:

- close the Phase 13 tranche
- add a new replay route
- widen Phase 13 into runtime HVC parity or broader security-policy ownership
- promote adjacent notifier evidence into a fifth helper family