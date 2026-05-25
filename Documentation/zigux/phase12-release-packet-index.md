# Phase 12 Release Packet Index

This note is the compact PMO packet index for the active Phase 12 release-planning tranche.

It exists to keep the shared release packet easy to reread from one place without widening release claims, reopening driver-local behavior, or inventing a new validation route.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_RELEASE_CLOSED=no`
- lane owner: `pmo-release`
- scope: phase sequencing, tranche-closure tracking, and release coordination for the shared Phase 12 packet on current `master`
- authority model: repo-first readback from current `master`, with the roadmap and ledger used only to keep the PMO packet bounded and truthful

## Shared PMO Packet

### Docs-root packet

The shared release-planning packet is currently anchored by:

- `Documentation/zigux/phase12-release-sequencing.md`
- `Documentation/zigux/phase12-release-readiness-survey.md`
- `Documentation/zigux/phase12-release-closure-checklist.md`
- `Documentation/zigux/phase12-release-coordination-matrix.md`
- `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`

### Scripts-root support bundle

The directly readable validator-first support bundle is currently:

- `scripts/zigux/validate-phase12.py`
- `scripts/zigux/check-build-only-phase12-surface.py`
- `scripts/zigux/check-phase12-release-readiness-packet.py`
- `scripts/zigux/check-phase12-complex-driver-lane-packet.py`
- `scripts/zigux/check-phase12-libbpf-snapshot.py`
- `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py`
- `scripts/zigux/check-phase12-virtio-scsi-libbpf-boundary.py`
- `scripts/zigux/README.md`

### Tests-root and workflow packet

The shared build-facing packet is currently:

- `zigux/tests/README.md`
- `zigux/tests/phase12_build.zig`
- `.github/workflows/zigux-bootstrap.yml`
- `zigux/Makefile`

The active shared `virtio_net` smoke-and-test sextet wired through `zigux/tests/phase12_build.zig` is:

- `zigux/tests/phase12_virtio_net_queue_resume.zig`
- `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`
- `zigux/tests/phase12_virtio_net_transmit_recycle.zig`
- `zigux/tests/phase12_virtio_net_post_reset_replay.zig`
- `zigux/tests/phase12_virtio_net_throughput_parity.zig`
- `zigux/tests/phase12_virtio_net_survey.zig`

### Shared wrapper evidence

Current `master` now exposes the full returned shared wrapper set again:

- `make -C zigux phase12-validate`
- `make -C zigux phase12-smoke`
- `make -C zigux phase12-test`
- `make -C zigux phase12`

Keep the validator-first then smoke-first order explicit when summarizing the shared packet.

## Adjacent But Not Shared Build Outputs

Keep these adjacent packets explicit without promoting them into the shared `smoke` or `test` route:

- `virtio_scsi` remains survey-backed and rollback-lab-only through `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, and `zigux/tests/phase12_virtio_scsi_survey_build.zig`
- `nvme_pci` remains a bounded driver-local foothold through `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `drivers/nvme/host/pci.zig`, `drivers/nvme/host/pci_verify.zig`, `zigux/tests/phase12_nvme_pci.zig`, `zigux/tests/phase12_nvme_pci_manifest.json`, and `zigux/tests/phase12_nvme_pci_survey.zig`
- the parked libbpf heavy-consumer packet remains note-owned through `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `zigux/tests/fixtures/phase12_libbpf_snapshot.json`, and `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json`

## Fallback Split

The degraded-read fallback split remains:

- commit-pinned direct replay catalog: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`
- driver-local current-master gap-inventory companion: `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
- shared-tree-only anchors: `Documentation/zigux/phase12-virtio-net-survey.md` and `Documentation/zigux/phase12-libbpf-segment-survey.md`
- shared-tree raw-read anchors during degraded contents reads: `zigux/tests/phase12_build.zig` and `scripts/zigux/check-build-only-phase12-surface.py`

## Release Boundaries

- This index is a coordination artifact, not a closure claim.
- Keep Phase 12 wording below DMA-safe receive ownership, queue-restart parity, deeper throughput delivery, recovery lifecycle, and transport-complete claims.
- `Documentation/zigux/freeze-map.md` remains the boundary owner for deeper `net/core/skbuff.c`, `kernel/workqueue.c`, and `kernel/trace/ring_buffer.c` anchors.
- Do not promote driver-local `virtio_scsi`, driver-local `nvme_pci`, or the parked libbpf packet into shared replay evidence unless new shared build wiring lands on current `master`.

## Next Bounded PMO Step

The next honest same-lane follow-through is reminder-side only:

- reread this index beside `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`
- reopen only if one of those shared PMO surfaces understates the directly readable support bundle, the returned wrapper set, or the six-file shared `virtio_net` packet
- leave fallback-only evidence refreshes to the neighboring fallback-overview lane unless they change the shared PMO packet itself
