# Phase 12 Release Sequencing

This note records the ordered release path for the active bounded Phase 12 tranche.

It is a release-coordination artifact, not a closure claim.

## Current posture
- `PHASE12_STATUS=active`
- `PHASE12_RELEASE_CLOSED=no`
- shared build replay entrypoint: `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
- Linux-style replay entrypoint: `make -C zigux phase12`
- shipped shared release surfaces on `master`: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-virtio-net-survey.md`, `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `scripts/zigux/README.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/README.md`, `zigux/tests/phase12_build.zig`, `zigux/Makefile`, the committed Phase 12 manifests under `zigux/tests/`, and `tools/lib/bpf/zigux_segments/manifest.json`
- current public fallback split: two commit-pinned artifacts (`Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`) and two shared-tree-only anchors (`virtio_net`, `libbpf`)
- current backlog evidence on `master` also includes validator-first Phase 12 artifacts that are real but not yet part of the shipped shared replay route: `Documentation/zigux/phase12-shared-replay-contract.md` and `scripts/zigux/validate-phase12.py`

## Release order
1. Reconfirm the shipped release packet surfaces before any replay claim.
   - Re-read `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `.github/workflows/zigux-bootstrap.yml`, and this sequencing note together.
   - These surfaces must continue to agree that the shipped shared replay route on `master` is the bounded `phase12_build.zig` plus `make -C zigux phase12` path, while `scripts/zigux/check-build-only-phase12-surface.py` plus `.github/workflows/zigux-bootstrap.yml` keep the build-only contract fail-closed.
2. Run the shipped shared Phase 12 build replay.
   - `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
   - This remains the shipped tranche-wide Zig replay surface for the bounded `virtio_net`, `nvme_pci`, `virtio_scsi`, and libbpf survey packet.
3. Run the Linux-style entrypoint last.
   - `make -C zigux phase12`
   - This should remain the summary replay route rather than the only place release coordination is inferred.
4. Treat validator-first evidence as separate backlog context until the route is actually wired.
   - `Documentation/zigux/phase12-shared-replay-contract.md` and `scripts/zigux/validate-phase12.py` now exist on `master` as real Phase 12 backlog evidence.
   - They are not yet the shipped shared replay route because `.github/workflows/zigux-bootstrap.yml` and `zigux/Makefile` still publish the build-and-make packet above rather than a `phase12-validate` entrypoint.

## Owner map
- `Network Driver Lane`: bounded `virtio_net` packet against `drivers/net/virtio_net.c`
- `Storage Driver Lane`: bounded `nvme_pci` and `virtio_scsi` packets against `drivers/nvme/host/pci.c` and `drivers/scsi/virtio_scsi.c`
- `BPF Tooling Lane`: bounded libbpf helper packet against `tools/lib/bpf/libbpf.c`
- `PMO / Release Management`: release-facing sequencing, tranche-readiness wording, and cross-surface coordination artifacts

## Current blocker to closure
The shared Phase 12 replay route on `master` is still narrower than the total Phase 12 evidence now present in the tree.

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
- `.github/workflows/zigux-bootstrap.yml`
- `zigux/tests/README.md`
- `zigux/tests/phase12_build.zig`
- `zigux/Makefile`
- the committed Phase 12 manifests under `zigux/tests/`
- `tools/lib/bpf/zigux_segments/manifest.json`
- the committed survey-backed test modules under `zigux/tests/`

The remaining release-discipline gap is therefore a packet-alignment problem rather than a driver-local blocker:
- `scripts/zigux/check-build-only-phase12-surface.py` is still the shipped build-only contract checker
- `.github/workflows/zigux-bootstrap.yml` still reruns that checker's self-test plus the live checker and remains the shipped automation surface for the current replay route
- `Documentation/zigux/phase12-shared-replay-contract.md` and `scripts/zigux/validate-phase12.py` are now real backlog evidence on `master`, but they are not yet wired into the primary shared replay route through `zigux/Makefile` or the workflow
- release planning should therefore distinguish between shipped replay surfaces and validator-first backlog evidence instead of describing the validator packet as either fully shipped or completely absent

## Closure conditions
Phase 12 should not be described as release-closed until all of the following are true:
1. `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/README.md`, and this sequencing note still agree on the same shipped Phase 12 replay surface.
2. `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-build-only-phase12-surface.py`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12` all remain explicit and green.
3. The approved four-anchor packet remains explicit and honest across the Phase 12 survey notes, the committed manifests under `zigux/tests/`, and `tools/lib/bpf/zigux_segments/manifest.json`.
4. The public fallback split is still described honestly, including `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, rather than rounded up into implied commit-pinned coverage for every anchor.
5. Any future validator-first Phase 12 release route is either wired into the primary shared replay path, or it remains described consistently as separate backlog evidence across the shared review packet.

## Next bounded PMO step
Keep the current Phase 12 PMO packet truthfulness-first.

The next same-lane follow-through should stay metadata-local:
- align `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and `scripts/zigux/check-build-only-phase12-surface.py` with this same shipped-route-versus-backlog-evidence distinction
- rerun `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test` and the live checker after those shared packet edits so the shipped build-only contract stays fail-closed
- avoid widening into any driver-local, helper-local, or validator-implementation work until the shared tranche wording is internally consistent again

If a validator-first release route is promoted later, land the actual workflow and Makefile entrypoints first, then update the release-planning notes to name that route exactly once beside the existing `phase12_build.zig` and `make -C zigux phase12` path.
