# Phase 12 Raw GitHub Coverage Survey

This note records the bounded public-read fallback posture for the roadmap-backed Phase 12 tranche.

## Scope

- lane: `P12-L07`
- phase: `Phase 12`
- public boundary: read-only GitHub tree and raw-path inspection only
- shared validator path: `python3 scripts/zigux/validate-phase12.py` and `make -C zigux phase12-validate`
- release coordination note: `Documentation/zigux/phase12-release-readiness-survey.md`
- release packet guard for this same split: `python3 scripts/zigux/check-phase12-release-readiness-packet.py`
- last replayed public head for this exact coverage split: `0bd402fd6ca83ba2ace6b21e9e57459401b631cd`

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

That split is the real current public boundary for this lane. It keeps the surviving `virtio_scsi` packet reviewable when connector-backed reads are flaky, preserves the archived `nvme_pci` raw-path packet, gives the shared-tree-only side one compact set of public readback roots plus one direct branch-tip raw path per remaining shared-tree-only anchor, and does not overstate equivalent live-head replay coverage for the other two Phase 12 anchors.

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

## Shared-Tree-Only Branch Raw Paths

Use these branch-tip raw paths when degraded review needs the remaining shared-tree-only anchor files directly instead of walking through the broader tree roots first:

- `virtio_net`: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/drivers/net/virtio_net.c`
- `libbpf`: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/tools/lib/bpf/libbpf.c`

These two raw paths stay intentionally weaker than the commit-pinned `virtio_scsi` catalog or the archived NVMe raw map. They are direct branch-tip pointers for the shared-tree-only anchors, not new commit-pinned fallback artifacts, and they should be read together with the tree roots above whenever the connector is flaky.

- `PHASE12_SHARED_TREE_BRANCH_RAW_PATH_COUNT=2`

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

The shared release-coordination reading for this same split now lives in `Documentation/zigux/phase12-release-readiness-survey.md`, and `python3 scripts/zigux/check-phase12-release-readiness-packet.py` keeps the release-facing PMO packet honest against that same mixed fallback split, so PMO review and degraded public-read review name the same two commit-pinned artifacts, the same two shared-tree-only anchors, the same two branch-tip shared-tree raw paths, and the same validator-first rollback path. That same release-facing prompt also remains visible in `Documentation/zigux/review-checklist.md`, so checklist-driven PMO review does not have to infer the mixed fallback split from the survey note alone. The adjacent shared-contract guard in `scripts/zigux/check-phase12-shared-replay-contract.py` already exact-counts the paired raw-coverage manifest and Zig-survey bullets published in `Documentation/zigux/phase12-shared-replay-contract.md`; the remaining stricter follow-up is therefore isolated to `scripts/zigux/check-phase12-release-readiness-packet.py`, which still treats the newer raw-coverage contract sentence plus the paired `zigux/tests/phase12_raw_github_coverage_manifest.json` and `zigux/tests/phase12_raw_github_coverage_survey.zig` Review Use bullets as presence-only today.
