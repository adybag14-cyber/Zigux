# Phase 12 Raw GitHub Coverage Survey

This note records the bounded public-read fallback posture for the roadmap-backed Phase 12 tranche.

## Scope

- lane: `P12-L07`
- phase: `Phase 12`
- public boundary: read-only GitHub tree and raw-path inspection only
- shared validator path: `python3 scripts/zigux/validate-phase12.py` and `make -C zigux phase12-validate`
- release coordination note: `Documentation/zigux/phase12-release-readiness-survey.md`
- release packet guard for this same split: `python3 scripts/zigux/check-phase12-release-readiness-packet.py`
- last replayed public head for this exact coverage split: `bc2373f7deedf021c73beaae29555a9ac6b0536d`

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

That split is the real current public boundary for this lane. It keeps the surviving `virtio_scsi` packet reviewable when connector-backed reads are flaky, preserves the archived `nvme_pci` raw-path packet, gives the shared-tree-only side one compact set of public readback roots, and does not overstate equivalent live-head replay coverage for the other two Phase 12 anchors.

- `PHASE12_ROADMAP_ANCHOR_COUNT=4`
- `PHASE12_COMMIT_PINNED_RAW_FALLBACK_COUNT=2`
- `PHASE12_SHARED_TREE_ONLY_FALLBACK_COUNT=2`
- `PHASE12_RELEASE_COORDINATION_SURVEY=Documentation/zigux/phase12-release-readiness-survey.md`

## Shared-Tree-Only Readback Roots

Use these stable tree roots when the connector can no longer keep `virtio_net` or `libbpf` readable enough for the shared-tree-only side of this packet:

- `https://github.com/adybag14-cyber/Zigux/tree/master/drivers/net`
- `https://github.com/adybag14-cyber/Zigux/tree/master/tools/lib/bpf`
- `https://github.com/adybag14-cyber/Zigux/tree/master/Documentation/zigux`
- `https://github.com/adybag14-cyber/Zigux/tree/master/zigux/tests`

Those four roots are intentionally smaller than the commit-pinned `virtio_scsi` catalog or the archived NVMe raw map. They keep the two shared-tree-only anchors reviewable without implying that `virtio_net` or `libbpf` already ship equivalent raw pinned packet coverage.

- `PHASE12_SHARED_TREE_READBACK_ROOT_COUNT=4`

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

The shared release-coordination reading for this same split now lives in `Documentation/zigux/phase12-release-readiness-survey.md`, and `python3 scripts/zigux/check-phase12-release-readiness-packet.py` keeps the release-facing PMO packet honest against that same mixed fallback split, so PMO review and degraded public-read review name the same two commit-pinned artifacts, the same two shared-tree-only anchors, and the same validator-first rollback path. That same release-facing prompt also remains visible in `Documentation/zigux/review-checklist.md`, so checklist-driven PMO review does not have to infer the mixed fallback split from the survey note alone. The adjacent shared-contract guard in `scripts/zigux/check-phase12-shared-replay-contract.py` already exact-counts the paired raw-coverage manifest and Zig-survey bullets published in `Documentation/zigux/phase12-shared-replay-contract.md`; the remaining stricter follow-up is therefore isolated to `scripts/zigux/check-phase12-release-readiness-packet.py`, which still treats that PMO-facing coupling as presence-only today.
