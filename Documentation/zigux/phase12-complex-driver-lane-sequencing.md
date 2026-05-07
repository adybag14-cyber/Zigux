# Phase 12 Complex Driver Lane Sequencing

This note records the bounded owner map for the active Phase 12 complex-driver lanes only.

It is an anti-overlap companion for the current tranche, not a release-order note, a libbpf packet, or a closure claim.

## Current posture
- `PHASE12_STATUS=active`
- complex-driver scope in this note: `virtio_net`, `nvme_pci`, and `virtio_scsi`
- excluded from this note on purpose: the shared PMO release packet and the non-driver libbpf helper packet
- shared replay routes that all three driver lanes may mention but do not own: `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12`
- shared coordination surfaces that stay non-owner here: `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/phase12_build.zig`, and `zigux/Makefile`

## Why this note exists

The Phase 12 roadmap names three high-risk driver anchors under one tranche: `drivers/net/virtio_net.c`, `drivers/nvme/host/pci.c`, and `drivers/scsi/virtio_scsi.c`.

Current `master` already keeps those lanes reviewable through one shared smoke-plus-build packet, but the live driver evidence is deliberately uneven:
- `virtio_net` is still survey-backed and shared-tree-only, with no separate slice note or commit-pinned fallback artifact on `master`
- `nvme_pci` has a dedicated slice note, survey note, commit-pinned raw GitHub fallback map, and a direct smoke verify shard
- `virtio_scsi` has a dedicated slice note, survey note, commit-pinned raw GitHub fallback catalog, and the current lab-only rollback drill

That asymmetry is honest, but it makes overlap easy unless the lane boundaries stay explicit.

## Driver lane map
- `virtio_net` lane:
  Owns `Documentation/zigux/phase12-virtio-net-survey.md`, `zigux/tests/phase12_virtio_net_manifest.json`, `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `zigux/tests/phase12_virtio_net_survey.zig`, and `drivers/net/virtio_net.zig`.
  The bounded live scope is the probe snapshot starter plus the directly coupled syntax-lab, queue-recovery, receive-refill, transmit-recycle, and mergeable-buffer-length follow-ups.
  It must stay below live DMA-backed runtime data-path work and must remain a shared-tree-only anchor unless a real commit-pinned fallback artifact lands.
- `nvme_pci` lane:
  Owns `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `zigux/tests/phase12_nvme_pci_manifest.json`, `zigux/tests/phase12_nvme_pci.zig`, `zigux/tests/phase12_nvme_pci_survey.zig`, `drivers/nvme/host/pci.zig`, and `drivers/nvme/host/pci_verify.zig`.
  The bounded live scope is the landed queue-count reservation, PRP buffer-shape, PRP metadata, recovery replay packet, and the direct verify shard that keeps that starter explicit inside the shared smoke packet.
  It stays parked unless the roadmap explicitly approves a transport-facing follow-up beyond that current storage-driver starter.
- `virtio_scsi` lane:
  Owns `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_survey.zig`, and `drivers/scsi/virtio_scsi.zig`.
  The bounded live scope is the landed queue-layout, probe-config snapshot, direct syntax-lab shard, and recovery packet, plus the lab-only rollback drill recorded in `Documentation/zigux/phase12-virtio-scsi-slice.md`.
  That rollback drill is storage-lane-local evidence, not a shared Phase 12 recovery claim.

## Shared non-owner surfaces
- `Documentation/zigux/phase12-release-sequencing.md` owns the release-order story for the tranche, not the next driver-local implementation step.
- `Documentation/zigux/phase12-release-closure-checklist.md` is the PMO closure companion, not a driver-lane planner.
- `Documentation/zigux/phase12-raw-github-coverage-survey.md` owns the mixed fallback-overview split for the active tranche, so driver lanes should reread it beside this note instead of treating it as a driver-local fallback artifact.
- `Documentation/zigux/phase12-release-coordination-matrix.md` keeps the compact lane-owner split, fallback split, and smoke-set summary explicit for PMO drift control, so driver lanes should reread it beside this note instead of leaving that compact release view implied from broader PMO prose.
- Driver-local survey notes that rely on this owner map should name `Documentation/zigux/phase12-complex-driver-lane-sequencing.md` explicitly instead of referring to an unnamed lane note, so the anti-overlap anchor stays discoverable from the active `virtio_net`, `nvme_pci`, and `virtio_scsi` packet.
- `scripts/zigux/check-build-only-phase12-surface.py` and `.github/workflows/zigux-bootstrap.yml` enforce the shared build-only review surface, not driver-local ownership.
- `Documentation/zigux/phase12-libbpf-segment-survey.md` and `tools/lib/bpf/zigux_segments/manifest.json` remain real Phase 12 evidence, but they belong to the non-driver helper packet and should not be absorbed into this driver-only map.

## Anti-overlap rules
- Do not let the `virtio_net` lane inherit the storage-lane fallback artifacts or the `virtio_scsi` rollback drill just because all three drivers share `phase12_build.zig`.
- Do not let the `nvme_pci` lane reuse `virtio_scsi` rollback wording as storage-wide recovery proof; its live packet is still the smaller queue-count, PRP-shape, PRP-metadata, recovery replay, and direct verify starter.
- Do not let the shared smoke packet turn `drivers/nvme/host/pci_verify.zig`, `zigux/tests/phase12_virtio_net_syntax_lab.zig`, or `zigux/tests/phase12_virtio_scsi_syntax_lab.zig` into tranche-wide evidence; those focused smoke shards remain lane-local proofs for `nvme_pci`, `virtio_net`, and `virtio_scsi` respectively.
- Do not let shared review surfaces collapse the active tranche to smoke-only shorthand; `zig build test --build-file zigux/tests/phase12_build.zig --summary all` and `make -C zigux phase12` remain part of the shipped shared replay order even while `drivers/nvme/host/pci_verify.zig`, `zigux/tests/phase12_virtio_net_syntax_lab.zig`, and `zigux/tests/phase12_virtio_scsi_syntax_lab.zig` stay lane-local smoke proofs.
- Do not let the `virtio_scsi` lane recast the `virtio_net` syntax-lab shard or the `nvme_pci` PRP helpers as shared storage evidence.
- Do not treat the shared smoke, build, Makefile, workflow, README, PMO notes, compact release-coordination matrix, or the shared raw-coverage overview as ownership transfer. Those surfaces coordinate the three driver lanes; they do not merge them.

## Next bounded step

Leave this note parked unless fresh repo inspection shows that the shared Phase 12 docs, fallback-overview, compact release-coordination matrix, or review surfaces are blurring `virtio_net`, `nvme_pci`, and `virtio_scsi` back together.

If the lane reopens, keep the next step inside the smallest docs-root, tests-root, fallback-overview, compact-matrix, or checker wording repair that restores those three driver-local ownership boundaries without reopening PMO closure drift control or the separate libbpf helper packet.
