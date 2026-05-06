# Phase 12 Release Closure Checklist

This checklist is the PMO release-closure companion to `Documentation/zigux/phase12-release-sequencing.md`.

It records what must stay true before the active bounded Phase 12 tranche can be described as release-closed.

It is not a closure claim, and it is not itself a shipped replay surface.

## Current status
- `PHASE12_STATUS=active`
- `PHASE12_RELEASE_CLOSED=no`
- sequencing authority: `Documentation/zigux/phase12-release-sequencing.md`
- shipped build-only contract checker: `scripts/zigux/check-build-only-phase12-surface.py`
- workflow replay anchor: `.github/workflows/zigux-bootstrap.yml`
- freeze-map boundary reminder: `Documentation/zigux/freeze-map.md` keeps `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` in boundary-study-only status, so this Phase 12 closure companion must not round queueing, rollback, or recovery wording up into deep-core delivery claims

## Shared replay order
1. `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
2. `make -C zigux phase12-smoke`
3. `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
4. `make -C zigux phase12`

## Closure checklist
1. Shared release surfaces still agree.
   - `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-virtio-net-survey.md`, `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `scripts/zigux/README.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/README.md`, `zigux/tests/phase12_build.zig`, and `zigux/Makefile` must still describe the same shipped Phase 12 replay packet.
   - Use this checklist as the PMO companion when judging whether those shipped surfaces are ready to be described as release-closed.
   - The shared checker and workflow must stay described as build-only contract enforcement rather than as a broader validator-first release gate.
   - There is still no shipped shared `scripts/zigux/validate-phase12.py`, `check-phase12-*.py`, or `make -C zigux phase12-validate` route on `master`.
2. Replay evidence stays green and explicit.
   - `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`
   - `python3 scripts/zigux/check-build-only-phase12-surface.py`
   - `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
   - `make -C zigux phase12-smoke`
   - `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
   - `make -C zigux phase12`
3. The approved four-anchor packet stays reviewable and honest.
   - The active tranche remains the shipped `nvme_pci`, `virtio_net`, `virtio_scsi`, and libbpf survey-backed packet described by the committed Phase 12 manifests under `zigux/tests/`, the committed Phase 12 survey-backed test modules under `zigux/tests/`, the focused direct smoke modules `zigux/tests/phase12_nvme_pci.zig`, `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_syntax_lab.zig`, and `zigux/tests/phase12_virtio_scsi.zig`, and `tools/lib/bpf/zigux_segments/manifest.json`.
   - The current driver-local doc split must stay explicit too: `nvme_pci` and `virtio_scsi` still ship dedicated slice-and-survey pairs, while `Documentation/zigux/phase12-virtio-net-survey.md` remains the truthful survey-only boundary until live `master` actually lands a separate `Documentation/zigux/phase12-virtio-net-slice.md` surface, even though the smoke-first replay already includes the direct `zigux/tests/phase12_virtio_net_syntax_lab.zig` shard.
   - The bounded `Documentation/zigux/phase12-virtio-scsi-slice.md` rollback drill must remain described as lab-only reversible-delivery evidence rather than closure-ready runtime recovery.
4. The public fallback split stays explicit.
   - Only `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` are commit-pinned fallback artifacts.
   - `Documentation/zigux/phase12-virtio-net-survey.md` and `Documentation/zigux/phase12-libbpf-segment-survey.md` remain shared-tree-only anchors rather than implied commit-pinned fallback coverage.
   - The sequencing note, this checklist, and the shared checker should continue to describe the smoke-first reminder consistently across those two commit-pinned fallback notes.
5. Future promotion rules stay honest.
   - If a validator-first or runtime-recovery Phase 12 release route is proposed later, the actual shipped file and replay surface must land on `master` before PMO notes describe it as active release evidence.
   - Until then, release planning should name only the shipped smoke preflight routes, the shared build-and-make replay path, the narrow build-only contract checker, and the bounded storage rollback drill.
   - `Documentation/zigux/freeze-map.md` must stay explicit here too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain boundary-study-only targets and are not part of the active Phase 12 complex-driver replay packet or closure evidence.

## Active release blocker
- Phase 12 is still an active release-planning tranche, not a release-closed packet.
- The remaining PMO job is drift control across the shipped docs-root, review checklist, `nvme_pci` slice-and-survey pair, the `virtio_net` survey-only boundary, `virtio_scsi` slice-and-survey pair, libbpf survey, scripts-root, tests-root, workflow, Makefile, `zigux/tests/phase12_nvme_pci.zig`, `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi.zig`, sequencing, this closure-checklist companion, and the two commit-pinned fallback-note surfaces so they keep naming the same bounded release route.
- `scripts/zigux/check-build-only-phase12-surface.py` still does not explicitly pin `Documentation/zigux/phase12-release-closure-checklist.md` inside its scripts-root marker set, so the closure companion is part of the shipped PMO packet but not yet fully fail-closed against scripts-root drift.
- Queueing and recovery language must keep the freeze-map split explicit: this release packet can describe bounded driver-local, libbpf, and lab-only rollback evidence, but it must not imply active delivery against `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`.
- This checklist should be refreshed whenever the shipped packet changes, but it should stay companion-scoped until the shared replay packet itself satisfies the closure conditions.
- Any future PMO follow-through should start by rerunning `scripts/zigux/check-build-only-phase12-surface.py` before widening into new wording or closure claims.
