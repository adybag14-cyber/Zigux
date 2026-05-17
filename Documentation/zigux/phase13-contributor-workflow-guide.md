# Phase 13 Contributor Workflow Guide

Use this guide when a change touches the active Phase 13 shared-helper packet and the review needs one contributor-facing workflow note instead of reconstructing the packet from scattered reminder surfaces.

This guide is a shared workflow companion. It is not a tranche-closure note, not a new replay route, and not a reason to collapse helper-local work into one generic Phase 13 bucket.

## Purpose

Keep broad contributor wording aligned with the active Phase 13 helper packet that currently stays centered on four roadmap-owned Linux anchors:

- `fs/libfs.c`
- `lib/devres.c`
- `security/landlock/ruleset.c`
- `security/landlock/syscalls.c`

Adjacent notifier evidence matters for release-surface truthfulness, but it is still adjacent evidence rather than a fifth helper family.

## Stable Shared Handle

Keep the broader contributor-facing shared reminder packet aligned through:

1. `Documentation/zigux/phase13-contributor-workflow-guide.md`
2. `scripts/zigux/README.md`
3. `zigux/tests/README.md`

Current `master` still does not materialize `zigux/Makefile`, `make -C zigux phase13-validate`, or `make -C zigux phase13`, so keep those older shared make-route names recorded as repo-reality gaps instead of folding them into the stable shared handle.

Current `master` still does not materialize `scripts/zigux/validate-phase13-release.py`, `scripts/zigux/check-phase13-devres-packet-alignment.py`, `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, or `scripts/zigux/check-phase13-shared-summary-surfaces.py`, so keep those older validator-first and checker names recorded as repo-reality gaps instead of folding them into the stable shared handle.

## Shared Surfaces To Reread Together

When shared Phase 13 wording changes, reread these contributor-facing surfaces together:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

If current `master` still does not materialize `scripts/zigux/validate-phase13-release.py`, `scripts/zigux/check-phase13-devres-packet-alignment.py`, `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, or `scripts/zigux/check-phase13-shared-summary-surfaces.py`, keep those checker names recorded as repo-reality gaps rather than rereadable shared surfaces.

Current `master` also still does not materialize `Documentation/zigux/phase13-notifier-list-survey.md`, so keep that note recorded as an adjacent repo-reality gap rather than a rereadable shared surface.

If one of those broad reminder surfaces changes, refresh the others before widening helper-local claims.

## Helper-Local Packets

Keep helper-local ownership explicit instead of flattening the packet into a single generic Phase 13 summary.

### `libfs`

Keep the shipped `libfs` foothold explicit through:

- `Documentation/zigux/phase13-libfs-survey.md`
- `fs/libfs.zig`
- `zigux/tests/phase13_libfs.zig`
- `zigux/tests/phase13_libfs_reviewability.zig`
- `zigux/tests/phase13_libfs_manifest.json`

Treat the older `Documentation/zigux/phase13-libfs-slice.md`, `zigux/tests/phase13_build.zig`, and `zigux/tests/phase13_libfs_addressability.zig` paths as repo-reality gaps until they materialize again on current `master`.

### `devres`

Keep the shipped `devres` packet explicit through:

- `Documentation/zigux/phase13-devres-slice.md`
- `Documentation/zigux/phase13-devres-survey.md`
- `lib/devres.zig`
- `zigux/tests/phase13_devres.zig`
- `zigux/tests/phase13_devres_reviewability.zig`
- `zigux/tests/phase13_devres_dma_coherent.zig`
- `zigux/tests/phase13_devres_boundary_evidence.zig`
- `zigux/tests/phase13_devres_manifest.json`

Keep the current helper-only DMA and scatterlist boundary explicit too: no DMA mapping helpers, no live scatterlist ownership, and no `sg_table` lifecycle control belong to the current packet. Treat older `scripts/zigux/check-phase13-devres-packet.py` wording and the missing `scripts/zigux/check-phase13-devres-packet-alignment.py` path as stale packet drift, not shipped current-`master` checker evidence.

### `landlock/ruleset`

Keep the shipped ruleset packet explicit through:

- `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
- `Documentation/zigux/phase13-landlock-ruleset-slice.md`
- `Documentation/zigux/phase13-landlock-ruleset-survey.md`
- `security/landlock/ruleset.zig`
- `zigux/tests/phase13_landlock_ruleset.zig`
- `zigux/tests/phase13_landlock_ruleset_manifest.json`

Treat the older `scripts/zigux/check-phase13-landlock-ruleset-packet.py` path as a repo-reality gap until current `master` materializes it again.

### `landlock/syscalls`

Keep the shipped syscall packet explicit through:

- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `security/landlock/syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
- `zigux/tests/phase13_landlock_syscalls_manifest.json`

Keep Landlock framed as shipped helper-local evidence, not as docs-only governance metadata.

### Adjacent Notifier Evidence

Current `master` still does not materialize `Documentation/zigux/phase13-notifier-list-survey.md`, so keep that survey note recorded as an adjacent repo-reality gap while keeping the shipped notifier support packet explicit through:

- `zigux/bindings/notifier_abi.zig`
- `zigux/helpers/notifier_chain_view.zig`
- `include/zigux/abi.h`
- `drivers/tty/hvc/hvc_console.h`

Treat notifier evidence as release-surface support rather than a fifth shared-helper anchor, and treat the older `scripts/zigux/check-phase13-notifier-priority-signal.py` path as a repo-reality gap until current `master` materializes it again.

## Shared Lane Split

Use the owner split from `Documentation/zigux/phase13-shared-helper-lane-sequencing.md` and keep the broad reminder lane narrow:

- helper-local `libfs`, `devres`, `landlock/ruleset`, and `landlock/syscalls` work should stay in their packet-local lanes
- shared contributor-surface truthfulness should stay in the broad reminder lane only
- this workflow guide should not absorb helper-local replays, helper growth, or packet-local survey repairs unless the broad reminder packet itself becomes untruthful without them

## Repo-Reality Gaps To Keep Honest

When contributor wording references absent direct companions, keep the absence explicit instead of presenting those paths as shipped evidence:

- `zigux/Makefile`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`
- `scripts/zigux/validate-phase13-release.py`
- `scripts/zigux/check-phase13-devres-packet-alignment.py`
- `scripts/zigux/check-phase13-landlock-ruleset-packet.py`
- `scripts/zigux/check-phase13-notifier-priority-signal.py`
- `scripts/zigux/check-phase13-shared-summary-surfaces.py`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `zigux/tests/phase13_build.zig`
- `Documentation/zigux/phase13-libfs-slice.md`
- `zigux/tests/phase13_libfs_addressability.zig`
- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `scripts/zigux/check-phase13-notifier-packet.py`
- `include/zigux/notifier_abi.h`
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`
- older `scripts/zigux/check-phase13-devres-packet.py`

## Reviewer Prompt

Before landing a broad Phase 13 reminder change, check that:

- the shared contributor surfaces still describe the same active-not-closed helper packet
- the stable shared handle still runs through the materialized `scripts/zigux/README.md` and `zigux/tests/README.md` reminder surfaces, while `zigux/Makefile`, `make -C zigux phase13-validate`, `make -C zigux phase13`, `scripts/zigux/validate-phase13-release.py`, `scripts/zigux/check-phase13-devres-packet-alignment.py`, `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, and `scripts/zigux/check-phase13-shared-summary-surfaces.py` stay explicit as repo-reality gaps
- `libfs`, `devres`, `landlock`, and adjacent notifier evidence still keep their separate owner maps
- repo-reality gaps stay explicit instead of being promoted into shipped current-`master` evidence

## Non-Goals

This guide does not:

- close the Phase 13 tranche
- add a new replay route
- widen Phase 13 into runtime HVC parity or broader security-policy ownership
- promote adjacent notifier evidence into a fifth helper family