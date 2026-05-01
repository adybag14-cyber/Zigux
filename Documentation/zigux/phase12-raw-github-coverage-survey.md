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

Current public-read coverage stays intentionally uneven:

- one anchor keeps a commit-pinned raw fallback catalog: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`
- three anchors remain shared-tree-only fallback reads: `virtio_net`, `nvme_pci`, and `libbpf`

That split is the real current public boundary for this lane. It keeps the surviving `virtio_scsi` packet reviewable when connector-backed reads are flaky, but it does not overstate equivalent raw fallback coverage for the other three Phase 12 anchors.

## Roadmap Comparison

- `virtio_net` is still visible through `Documentation/zigux/phase12-virtio-net-survey.md`, but it does not yet ship a commit-pinned raw fallback catalog parallel to the `virtio_scsi` packet.
- `nvme_pci` is still visible through `Documentation/zigux/phase12-nvme-pci-survey.md`, but it also remains a shared-tree-only fallback read.
- `virtio_scsi` is the only Phase 12 anchor that currently ships both a survey packet and a commit-pinned raw fallback catalog.
- `libbpf` stays visible through `Documentation/zigux/phase12-libbpf-segment-survey.md`, but its public-read fallback posture is still shared-tree-only rather than catalog-pinned.

## Why This Matters

The roadmap still expects honest segmented rollout and reviewability for complex drivers and heavy helper consumers. This survey keeps the current public-read posture explicit without widening into DMA-backed queue ownership, NVMe execution flow, SCSI host lifecycle work, or libbpf object-model follow-up.

The surviving `virtio_scsi` fallback catalog remains the exact packet this survey compares against:

- `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`
