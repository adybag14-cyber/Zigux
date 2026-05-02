# Phase 12 Raw GitHub Coverage Survey

This note records the bounded public-read fallback posture for the roadmap-backed Phase 12 tranche.

## Scope

- lane: `P12-L07`
- phase: `Phase 12`
- public boundary: read-only GitHub tree and raw-path inspection only
- last replayed public head for this exact coverage split: `a8daee106057a542aa03f2983662bec7c06584bb`

## Coverage Split

The Phase 12 roadmap still names four anchors:

- `drivers/net/virtio_net.c`
- `drivers/nvme/host/pci.c`
- `drivers/scsi/virtio_scsi.c`
- `tools/lib/bpf/libbpf.c`

Current public-read coverage stays intentionally mixed:

- one anchor keeps a commit-pinned raw fallback catalog with a last bounded replay note: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`
- one anchor keeps a commit-pinned raw fallback map for the archived NVMe packet: `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
- two anchors remain shared-tree-only fallback reads: `virtio_net` and `libbpf`

That split is the real current public boundary for this lane. It keeps the surviving `virtio_scsi` packet reviewable when connector-backed reads are flaky, preserves the archived `nvme_pci` raw-path packet, and does not overstate equivalent live-head replay coverage for the other two Phase 12 anchors.

## Roadmap Comparison

- `virtio_net` is still visible through `Documentation/zigux/phase12-virtio-net-survey.md`, but it does not yet ship a commit-pinned raw fallback artifact parallel to the `virtio_scsi` or `nvme_pci` packets.
- `nvme_pci` is still visible through `Documentation/zigux/phase12-nvme-pci-survey.md`, and it now also ships `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` for the archived packet, but that map intentionally stays archival rather than claiming a live-head replay catalog parallel to `virtio_scsi`.
- `virtio_scsi` is the only Phase 12 anchor that currently ships both a survey packet and a commit-pinned raw fallback catalog with a recorded bounded replay note.
- `libbpf` stays visible through `Documentation/zigux/phase12-libbpf-segment-survey.md`, but its public-read fallback posture is still shared-tree-only rather than map-pinned or catalog-pinned.

## Why This Matters

The roadmap still expects honest segmented rollout and reviewability for complex drivers and heavy helper consumers. This survey keeps the current public-read posture explicit without widening into DMA-backed queue ownership, NVMe execution flow, SCSI host lifecycle work, or libbpf object-model follow-up.

The surviving pinned fallback artifacts this survey compares against remain:

- `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`
- `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
