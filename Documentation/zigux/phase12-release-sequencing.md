# Phase 12 Release Sequencing

This note records the ordered release path for the active bounded Phase 12 tranche.

It is a release-coordination artifact, not a closure claim.

## Current posture

- `PHASE12_STATUS=active`
- `PHASE12_RELEASE_CLOSED=no`
- shared build replay entrypoint: `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
- Linux-style replay entrypoint: `make -C zigux phase12`
- shipped shared release surfaces on `master`: `Documentation/zigux/README.md`, `Documentation/zigux/phase12-release-sequencing.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/tests/phase12_build.zig`, `zigux/Makefile`, and the committed Phase 12 manifests under `zigux/tests/`
- current public fallback split: two commit-pinned artifacts (`nvme_pci`, `virtio_scsi`) and two shared-tree-only anchors (`virtio_net`, `libbpf`)

## Release order

1. Reconfirm the release packet surfaces before any replay claim.
   - Re-read `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and this sequencing note together.
   - These surfaces must continue to agree that the shared replay route on `master` is the bounded `phase12_build.zig` plus `make -C zigux phase12` path, not an unshipped dedicated checker or shared validator stack.

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
- `Documentation/zigux/phase12-release-sequencing.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `zigux/tests/phase12_build.zig`
- `zigux/Makefile`
- the committed Phase 12 manifests and survey-backed test modules under `zigux/tests/`

The remaining release-discipline gap is still a PMO truthfulness problem rather than a closure-ready checkpoint:

- there is no shipped shared `scripts/zigux/validate-phase12.py`, no `check-phase12-*.py` release packet, and no `make -C zigux phase12-validate` target on `master`
- release planning must therefore keep naming only the shipped build-and-make replay path until a validator-first Phase 12 packet actually lands

## Closure conditions

Phase 12 should not be described as release-closed until all of the following are true:

1. `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and this sequencing note still agree on the same shipped Phase 12 replay surface.
2. `zig build test --build-file zigux/tests/phase12_build.zig --summary all` and `make -C zigux phase12` both remain explicit and green.
3. The approved four-anchor packet remains explicit and honest across the Phase 12 survey notes and manifests.
4. The public fallback split is still described honestly rather than rounded up into implied commit-pinned coverage for every anchor.
5. Any future validator-first Phase 12 release gate is published on `master` before PMO notes describe it as part of the active release route.

## Next bounded PMO step

Keep the current Phase 12 PMO packet truthfulness-first.

If a validator-first release route is proposed later, land the actual shipped file and replay surface first, then update the release-planning notes to name it exactly once beside the existing `phase12_build.zig` and `make -C zigux phase12` path.
