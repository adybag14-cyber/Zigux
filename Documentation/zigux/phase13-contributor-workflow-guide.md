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

Keep `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/phase13-shared-summary-guard-gap.md`, and `Documentation/zigux/phase13-notifier-summary-gap.md` aligned with that stable handle as supporting shared reminder surfaces.

Keep `Documentation/zigux/phase13-release-coordination-matrix.md` and `Documentation/zigux/phase13-shared-helper-lane-sequencing.md` aligned as supporting shared reminder surfaces rather than as the stable contributor-facing handle itself.

Keep `Documentation/zigux/phase13-release-notes-survey.md` and `Documentation/zigux/phase13-roadmap-traceability.md` aligned as broader same-lane reminder surfaces rather than as the stable contributor-facing handle itself.

stable shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`
tests-root alignment companion: `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`
release-discipline validator: `python3 scripts/zigux/validate-phase13-release.py`

Keep `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py` explicit as the shipped shared-summary guard for those reminder surfaces rather than as the contributor-facing handle itself.

Keep `python3 scripts/zigux/check-phase13-tests-readme-alignment.py` explicit as the shipped tests-root alignment companion for that stable handle rather than as a new replay route or a Makefile-backed entrypoint.

Keep `python3 scripts/zigux/validate-phase13-release.py` explicit as the shipped release-discipline validator for that stable handle rather than as a new replay route or a Makefile-backed entrypoint.

`zigux/Makefile` is present on current `master`, but it still does not expose `make -C zigux phase13-validate` or `make -C zigux phase13`, so keep the file itself distinct from those missing Phase 13 route names and keep only the route names recorded as repo-reality gaps until the shared build handle returns.

## Docs-Root Companion

Current `master` now includes a dedicated Phase 13 reminder block in `Documentation/zigux/README.md`.

Keep that docs-root block aligned as the broader docs-root companion for this lane:

1. keep the stable contributor-facing handle anchored to `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`
2. keep `Documentation/zigux/README.md` aligned as a broader same-lane reminder surface rather than a substitute for the stable contributor-facing handle
3. if the docs-root Phase 13 block drifts, land that as one shared reminder-surface refresh instead of widening a helper-local packet

Docs-root companion rule: because `Documentation/zigux/README.md` now carries a dedicated Phase 13 reminder block on current `master`, keep it aligned as broader docs-root support for the workflow-guide, scripts-root, and tests-root trio rather than treating it as missing or as the stable contributor-facing handle itself.

## Degraded-Read Fallback

When local checkout access or authenticated blob rereads are unavailable, keep shared Phase 13 workflow work bounded to the stable contributor-facing handle plus only the exact helper-local note you are touching.

1. reread `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` first
2. use authenticated GitHub reads for those three files plus the exact helper-local Phase 13 path you plan to change
3. if authenticated reads degrade, fall back to the exact public GitHub page or raw GitHub URL for only those same paths
4. keep `zigux/Makefile`, `make -C zigux phase13-validate`, `make -C zigux phase13`, `zigux/tests/phase13_build.zig`, and helper-local manifest gaps framed as repo-reality gaps unless the same run directly rereads them successfully
5. if local reruns are unavailable after the reread, record validation as exact readback only instead of implying a shipped replay route

Degraded-read fallback rule: if local checkout access or authenticated blob reads are unavailable, reread `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and only the exact helper-local Phase 13 note you are touching through authenticated GitHub reads first and raw GitHub fallback second, then keep any still-absent route or helper in the repo-reality-gap bucket instead of promoting it into shipped evidence.

## Contributor Quick Start

If this is your first Phase 13 reminder-surface edit in a while, use this short loop before reading the longer packet details:

1. open `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` together
2. decide whether the change is shared contributor wording or helper-local proof, and stay on the shared side unless the packet forces a narrower helper note
3. edit at most one shared reminder surface plus the smallest helper-local note needed to keep the packet truthful
4. rerun `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`, `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`, and `python3 scripts/zigux/validate-phase13-release.py`
5. leave any absent route, replay, or helper framed as a repo-reality gap instead of promoting it into shipped evidence

Contributor quick-start loop: open the workflow-guide, scripts-root, and tests-root trio first, keep the change to one shared reminder surface plus the smallest helper-local note, rerun the shared-summary, tests-root, and release-validator trio, and leave missing routes or helpers in the repo-reality-gap bucket.

## Pre-Edit Triage Checklist

Before changing a shared Phase 13 reminder surface, answer these three questions in order:

1. is this a shared contributor wording repair, or is it really helper-local proof owned by `libfs`, `devres`, or `landlock`?
2. if helper-local evidence must move, can the change stay inside one helper packet instead of widening the shared reminder packet?
3. if the supporting route, replay, or checker is absent on current `master`, should it stay recorded as a repo-reality gap instead of being promoted into shipped evidence?

Pre-edit triage rule: classify the work as shared contributor wording, one helper-local packet, or repo-reality-gap follow-through before editing, and if a supporting route or replay is absent on current `master`, leave it in the gap bucket instead of promoting it into shipped evidence.

## Shared Surfaces To Reread Together

When shared Phase 13 wording changes, reread these contributor-facing and support surfaces together:

- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-shared-summary-guard-gap.md`
- `Documentation/zigux/phase13-notifier-summary-gap.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `scripts/zigux/check-phase13-shared-summary-surfaces.py`
- `scripts/zigux/check-phase13-tests-readme-alignment.py`
- `scripts/zigux/validate-phase13-release.py`

Keep broader docs-root refresh as a separate same-lane follow-up instead of mixing it into helper-local packet work.

## Contributor Edit Loop

When the change stays inside the shared Phase 13 reminder lane, use this bounded edit loop:

1. reread `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` together before touching helper-local wording
2. update at most one shared reminder surface plus the smallest necessary helper-local packet note in the same change
3. rerun `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`, `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`, and `python3 scripts/zigux/validate-phase13-release.py`
4. if a route, replay, or helper is absent on current `master`, keep it recorded as a repo-reality gap instead of promoting it into shipped evidence

Shared contributor edit loop: reread `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` together first, update at most one shared reminder surface plus the smallest helper-local packet note in the same change, rerun `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`, `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`, and `python3 scripts/zigux/validate-phase13-release.py`, and keep any absent route, replay, or helper recorded as a repo-reality gap instead of promoted shipped evidence.

## Helper-Local Packets

Keep helper-local ownership explicit instead of flattening the packet into a single generic Phase 13 summary.

### `libfs`

- `Documentation/zigux/phase13-libfs-slice.md`
- `fs/libfs.zig`
- `zigux/tests/phase13_libfs.zig`
- `zigux/tests/phase13_libfs_reviewability.zig`
- `zigux/tests/phase13_libfs_manifest.json`

Keep `Documentation/zigux/phase13-libfs-survey.md`, `zigux/tests/phase13_libfs_addressability.zig`, and `zigux/tests/phase13_build.zig` recorded as repo-reality gaps until they rematerialize on current `master`, while `Documentation/zigux/phase13-libfs-slice.md` stays explicit as the bounded helper-scope note for the live `libfs` packet.

### `devres`

- `Documentation/zigux/phase13-devres-slice.md`
- `Documentation/zigux/phase13-devres-survey.md`
- `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`
- `Documentation/zigux/phase13-devres-iounmap-planner.md`
- `Documentation/zigux/phase13-devres-iomap-planner.md`
- `Documentation/zigux/phase13-devres-scatterlist-slice.md`
- `Documentation/zigux/phase13-devres-scatterlist-planner.md`
- `scripts/zigux/check-phase13-devres-dma-boundary.py`
- `scripts/zigux/check-phase13-devres-dmam-alloc-coherent-planner.py`
- `scripts/zigux/check-phase13-devres-iounmap-planner.py`
- `scripts/zigux/check-phase13-devres-iomap-planner.py`
- `scripts/zigux/check-phase13-devres-mmio-packet.py`
- `scripts/zigux/check-phase13-devres-current-packet.py`
- `scripts/zigux/check-phase13-devres-scatterlist-planner.py`
- `zigux/tests/phase13_devres_dma_coherent.zig`
- `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`
- `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`
- `zigux/tests/phase13_devres_dmam_alloc_zero_size_replay_build.zig`
- `zigux/tests/phase13_devres_iounmap_planner.zig`
- `zigux/tests/phase13_devres_iounmap_planner_manifest.json`
- `zigux/tests/phase13_devres_iomap_planner.zig`
- `zigux/tests/phase13_devres_iomap_planner_manifest.json`
- `zigux/tests/phase13_devres_scatterlist_planner_manifest.json`
- `lib/devres.zig`
- `lib/devres_scatterlist.zig`
- `zigux/tests/phase13_devres_scatterlist.zig`
- `zigux/tests/phase13_devres_scatterlist_build.zig`

Keep `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_manifest.json`, `scripts/zigux/check-phase13-devres-packet.py`, and `scripts/zigux/check-phase13-devres-packet-alignment.py` recorded as repo-reality gaps until they rematerialize on current `master`.

### `landlock/ruleset`

- `Documentation/zigux/phase13-landlock-ruleset-survey.md`
- `security/landlock/ruleset.zig`
- `zigux/tests/phase13_landlock_ruleset.zig`
- `zigux/tests/phase13_landlock_ruleset_manifest.json`
- `scripts/zigux/check-phase13-landlock-ruleset-packet.py`

Keep `Documentation/zigux/phase13-landlock-ruleset-slice.md` and `Documentation/zigux/phase13-landlock-ruleset-ownership.md` recorded as repo-reality gaps until they rematerialize on current `master`.

### `landlock/syscalls`

- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `Documentation/zigux/phase13-landlock-syscalls-survey-gap.md`
- `scripts/zigux/check-phase13-landlock-syscalls-packet.py`
- `security/landlock/syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`

Keep `zigux/tests/phase13_landlock_syscalls_manifest.json` and `zigux/tests/phase13_build.zig` recorded as repo-reality gaps until they rematerialize on current `master`, while the direct replay and reviewability companions stay explicit as shipped current-`master` evidence.

## Adjacent Notifier Evidence

Keep notifier evidence explicit as adjacent release-surface support through:

- `Documentation/zigux/phase13-notifier-list-survey.md`
- `scripts/zigux/check-phase13-notifier-packet.py`
- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `zigux/bindings/notifier_abi.zig`
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`
- `include/zigux/abi.h`
- `drivers/tty/hvc/hvc_console.h`

Keep `zigux/helpers/notifier_chain_view.zig`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, and `include/zigux/notifier_abi.h` recorded as repo-reality gaps until they rematerialize on current `master`. `zigux/Makefile` is present again, but `make -C zigux phase13-validate` and `make -C zigux phase13` still remain repo-reality-gap route names until that Phase 13 shared build handle is restored.

## Reviewer Prompt

Before landing a broad Phase 13 reminder change, check that:

- the contributor-facing handle still runs through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`
- `Documentation/zigux/review-checklist.md` and `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md` stay aligned as the supporting shared reminder surfaces for that stable handle
- the release-coordination matrix and shared-helper sequencing note still describe the same active helper packet
- the stable shared-summary guard remains `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`
- the shipped tests-root alignment companion remains `python3 scripts/zigux/check-phase13-tests-readme-alignment.py` so the broader contributor wording and the tests-root reminder stay on the same Phase 13 packet
- the shipped release-discipline validator remains `python3 scripts/zigux/validate-phase13-release.py` so contributor workflow wording keeps the same shared release support named across the live Phase 13 reminder surfaces
- helper-local owner maps for `libfs`, `devres`, and `landlock` remain explicit
- the shipped `devres` packet still runs through `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `Documentation/zigux/phase13-devres-iounmap-planner.md`, `Documentation/zigux/phase13-devres-iomap-planner.md`, `Documentation/zigux/phase13-devres-scatterlist-slice.md`, `Documentation/zigux/phase13-devres-scatterlist-planner.md`, `scripts/zigux/check-phase13-devres-dma-boundary.py`, `scripts/zigux/check-phase13-devres-dmam-alloc-coherent-planner.py`, `scripts/zigux/check-phase13-devres-iounmap-planner.py`, `scripts/zigux/check-phase13-devres-iomap-planner.py`, `scripts/zigux/check-phase13-devres-mmio-packet.py`, `scripts/zigux/check-phase13-devres-current-packet.py`, `scripts/zigux/check-phase13-devres-scatterlist-planner.py`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `zigux/tests/phase13_devres_dmam_alloc_zero_size_replay_build.zig`, `zigux/tests/phase13_devres_iounmap_planner.zig`, `zigux/tests/phase13_devres_iounmap_planner_manifest.json`, `zigux/tests/phase13_devres_iomap_planner.zig`, `zigux/tests/phase13_devres_iomap_planner_manifest.json`, `zigux/tests/phase13_devres_scatterlist_planner_manifest.json`, `lib/devres.zig`, `lib/devres_scatterlist.zig`, `zigux/tests/phase13_devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist_build.zig`, while `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_manifest.json`, `scripts/zigux/check-phase13-devres-packet.py`, and `scripts/zigux/check-phase13-devres-packet-alignment.py` stay recorded as repo-reality gaps rather than shipped current-`master` evidence
- adjacent notifier evidence stays adjacent rather than becoming a fifth helper family
- the shipped notifier survey, focused checker, manifest, reviewability gate, `zigux/bindings/notifier_abi.zig`, and the `list_view` and `hlist_view` helpers stay explicit as adjacent evidence without being promoted into the shared helper handle
- `zigux/helpers/notifier_chain_view.zig`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, and `include/zigux/notifier_abi.h` stay recorded as repo-reality gaps, while `zigux/Makefile` stays distinguished from the still-missing `make -C zigux phase13-validate` and `make -C zigux phase13` route names instead of promoting that partial build surface into shipped current-`master` Phase 13 evidence
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-survey-gap.md`, `scripts/zigux/check-phase13-landlock-syscalls-packet.py`, `security/landlock/syscalls.zig`, `zigux/tests/phase13_landlock_syscalls.zig`, and `zigux/tests/phase13_landlock_syscalls_reviewability.zig` stay explicit as the current Landlock syscall helper-local packet while `zigux/tests/phase13_landlock_syscalls_manifest.json` and `zigux/tests/phase13_build.zig` stay recorded as repo-reality gaps rather than shipped current-`master` evidence

## Non-Goals

This guide does not:

- close the Phase 13 tranche
- add a new replay route
- widen Phase 13 into runtime HVC parity or broader security-policy ownership
- promote adjacent notifier evidence into a fifth helper family
