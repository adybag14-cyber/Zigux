# Phase 12 Release Closure Checklist

This checklist is the PMO release-closure companion to `Documentation/zigux/phase12-release-sequencing.md`.

It records what must stay true before the active bounded Phase 12 tranche can be described as release-closed.

It is not a closure claim.

## Current status
- `PHASE12_STATUS=active`
- `PHASE12_RELEASE_CLOSED=no`
- sequencing authority: `Documentation/zigux/phase12-release-sequencing.md`
- shipped build-only contract checker: `scripts/zigux/check-build-only-phase12-surface.py`
- workflow replay anchor: `.github/workflows/zigux-bootstrap.yml`

## Shared replay order
1. `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
2. `make -C zigux phase12-smoke`
3. `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
4. `make -C zigux phase12`

## Closure checklist
1. Shared release surfaces still agree.
   - `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, this checklist, `scripts/zigux/README.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/README.md`, `zigux/tests/phase12_build.zig`, and `zigux/Makefile` must still describe the same shipped Phase 12 replay packet.
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
   - The active tranche remains the shipped `nvme_pci`, `virtio_net`, `virtio_scsi`, and libbpf survey-backed packet described by the committed Phase 12 manifests under `zigux/tests/`, the committed Phase 12 survey-backed test modules under `zigux/tests/`, and `tools/lib/bpf/zigux_segments/manifest.json`.
   - The bounded `Documentation/zigux/phase12-virtio-scsi-slice.md` rollback drill must remain described as lab-only reversible-delivery evidence rather than closure-ready runtime recovery.
4. The public fallback split stays explicit.
   - Only `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` are commit-pinned fallback artifacts.
   - `virtio_net` and libbpf remain shared-tree-only anchors rather than implied commit-pinned fallback coverage.
   - The sequencing note, this checklist, and the shared checker must keep the smoke-first reminder aligned across those two commit-pinned fallback notes.
5. Future promotion rules stay honest.
   - If a validator-first or runtime-recovery Phase 12 release route is proposed later, the actual shipped file and replay surface must land on `master` before PMO notes describe it as active release evidence.
   - Until then, release planning should name only the shipped smoke preflight routes, the shared build-and-make replay path, the narrow build-only contract checker, and the bounded storage rollback drill.

## Active release blocker
- Phase 12 is still an active release-planning tranche, not a release-closed packet.
- The remaining PMO job is drift control across the shipped docs-root, checklist, scripts-root, tests-root, workflow, Makefile, sequencing, and fallback-note surfaces so they keep naming the same bounded release route.
- Any future PMO follow-through should start by rerunning `scripts/zigux/check-build-only-phase12-surface.py` before widening into new wording or closure claims.
