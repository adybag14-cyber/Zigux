# Phase 12 Release Sequencing

This note records the ordered release path for the active bounded Phase 12 tranche.

It is a release-coordination artifact, not a closure claim.

## Current posture

- `PHASE12_STATUS=active`
- `PHASE12_RELEASE_CLOSED=no`
- shared build replay entrypoint: `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
- Linux-style replay entrypoint: `make -C zigux phase12`
- shipped shared release surfaces on `master`: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-virtio-net-survey.md`, `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `scripts/zigux/README.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `zigux/tests/README.md`, `zigux/tests/phase12_build.zig`, `zigux/Makefile`, the committed Phase 12 manifests under `zigux/tests/`, and `tools/lib/bpf/zigux_segments/manifest.json`
- current public fallback split: two commit-pinned artifacts (`Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`) and two shared-tree-only anchors (`virtio_net`, `libbpf`)

## Release order

1. Reconfirm the release packet surfaces before any replay claim.
   - Re-read `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and this sequencing note together.
   - These surfaces must continue to agree that the shared replay route on `master` is the bounded `phase12_build.zig` plus `make -C zigux phase12` path, and `scripts/zigux/check-build-only-phase12-surface.py` must continue to keep that build-only contract fail-closed rather than implying an unshipped validator stack.

2. Run the shared Phase 12 build replay.
   - `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
   - This remains the shipped tranche-wide Zig replay surface for the bounded `virtio_net`, `nvme_pci`, `virtio_scsi`, and libbpf survey packet.

3. Run the Linux-style entrypoint last.
   - `make -C zigux phase12`
   - This should remain the summary replay route rather than the only place release coordination is inferred.

## Owner map

- `Network Driver Lane`: bounded `virtio_net` packet against `drivers/net/virtio_net.c`
- `Storage Driver Lane`: bounded `nvme_pci` and `virtio_scsi` packets against `drivers/nvme/host/pci.c` and `drivers/scsi/virtio_scsi.c`
- `BPF Tooling Lane`: bounded libbpf helper packet against `tools/lib/bpf/libbpf.c`
- `PMO / Release Management`: release-facing sequencing, tranche-readiness wording, and cross-surface coordination artifacts

## Current blocker to closure

The shared Phase 12 replay route on `master` is narrower than some older PMO notes implied.

Today the shipped release packet is centered on:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase12-release-sequencing.md`
- `Documentation/zigux/phase12-nvme-pci-slice.md`
- `Documentation/zigux/phase12-nvme-pci-survey.md`
- `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
- `Documentation/zigux/phase12-virtio-net-survey.md`
- `Documentation/zigux/phase12-virtio-scsi-slice.md`
- `Documentation/zigux/phase12-virtio-scsi-survey.md`
- `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`
- `Documentation/zigux/phase12-libbpf-segment-survey.md`
- `scripts/zigux/README.md`
- `scripts/zigux/check-build-only-phase12-surface.py`
- `zigux/tests/README.md`
- `zigux/tests/phase12_build.zig`
- `zigux/Makefile`
- the committed Phase 12 manifests under `zigux/tests/`
- `tools/lib/bpf/zigux_segments/manifest.json`
- the committed survey-backed test modules under `zigux/tests/`

The remaining release-discipline gap is still a PMO truthfulness problem rather than a closure-ready checkpoint:

- `scripts/zigux/check-build-only-phase12-surface.py` is a shipped build-only contract checker, not a broader validator-first release gate
- there is no shipped shared `scripts/zigux/validate-phase12.py`, no `check-phase12-*.py` release packet, and no `make -C zigux phase12-validate` target on `master`
- release planning must therefore keep naming only the shipped build-and-make replay path plus the narrow build-only contract checker until a validator-first Phase 12 packet actually lands

## Closure conditions

Phase 12 should not be described as release-closed until all of the following are true:

1. `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `zigux/tests/README.md`, and this sequencing note still agree on the same shipped Phase 12 replay surface.
2. `zig build test --build-file zigux/tests/phase12_build.zig --summary all` and `make -C zigux phase12` both remain explicit and green.
3. The approved four-anchor packet remains explicit and honest across the Phase 12 survey notes, the committed manifests under `zigux/tests/`, and `tools/lib/bpf/zigux_segments/manifest.json`.
4. The public fallback split is still described honestly, including `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, rather than rounded up into implied commit-pinned coverage for every anchor.
5. Any future validator-first Phase 12 release gate is published on `master` before PMO notes describe it as part of the active release route, while `scripts/zigux/check-build-only-phase12-surface.py` remains scoped to the shipped build-only contract.

## Next bounded PMO step

Keep the current Phase 12 PMO packet truthfulness-first.

The scripts-root wording repair is already landed on `master`, so the next bounded same-lane follow-through is to keep the sequencing note and the shipped checker-backed replay contract aligned:

- when Phase 12 release-facing wording changes, rerun `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test` and the live checker before widening any PMO claim
- keep this sequencing note aligned with `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` instead of reopening the already-landed scripts-root naming repair

If a validator-first release route is proposed later, land the actual shipped file and replay surface first, then update the release-planning notes to name it exactly once beside the existing `phase12_build.zig` and `make -C zigux phase12` path.
