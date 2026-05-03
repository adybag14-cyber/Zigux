# Phase 12 Release Readiness Survey

This document records the current release-discipline reading for the active bounded Phase 12 complex-driver tranche without claiming that the roadmap phase is globally closed.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_TRANCHE=driver-and-libbpf-survey-bundle`
- `PHASE12_RELEASE_SURVEY=present`
- `PHASE12_SHARED_VALIDATE_ENTRYPOINT=make -C zigux phase12-validate`
- `PHASE12_SHARED_REPLAY_ENTRYPOINT=make -C zigux phase12`
- scope: roadmap-backed `virtio_net`, `nvme_pci`, `virtio_scsi`, and bounded libbpf helper evidence plus the current cross-compile smoke packet and the mixed public-read fallback coverage packet
- product boundary:
  - `Documentation/zigux/phase12-release-readiness-survey.md`
  - `Documentation/zigux/phase12-cross-compile-smoke.md`
  - `Documentation/zigux/phase12-raw-github-coverage-survey.md`
  - `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
  - `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`
  - `Documentation/zigux/phase12-virtio-net-survey.md`
  - `Documentation/zigux/phase12-nvme-pci-survey.md`
  - `Documentation/zigux/phase12-nvme-pci-slice.md`
  - `Documentation/zigux/phase12-virtio-scsi-survey.md`
  - `Documentation/zigux/phase12-virtio-scsi-slice.md`
  - `Documentation/zigux/phase12-libbpf-segment-survey.md`
  - `scripts/zigux/check-phase12-cross.py`
  - `scripts/zigux/check-phase12-libbpf-focused-replay.py`
  - `scripts/zigux/validate-phase12.py`
  - `zigux/tests/phase12_cross_build.zig`
  - `zigux/tests/phase12_libbpf_only_build.zig`
  - `zigux/tests/phase12_build.zig`
  - `zigux/Makefile`

## Why this record exists

The live repo already carries real Phase 12 survey notes, shared validation wiring, a bounded cross-compile smoke packet, and a mixed raw-GitHub fallback packet. What it did not yet have was one release-facing note that says, in one place, how those pieces should be read together.

This survey closes that PMO gap without widening driver scope:

- the current tranche is active, not closed
- the shared validator-first path remains `python3 scripts/zigux/validate-phase12.py`, `make -C zigux phase12-validate`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12`
- the non-native compile-smoke packet is an explicit part of the release reading through `Documentation/zigux/phase12-cross-compile-smoke.md`, `python3 scripts/zigux/check-phase12-cross.py --zig <zig-path>`, and `zigux/tests/phase12_cross_build.zig`
- the public-read fallback posture is intentionally mixed and should stay explicit instead of being inferred from whichever anchor most recently gained a pinned raw catalog
- the release packet should say plainly which anchors have commit-pinned public fallback artifacts today and which still rely on shared-tree fallback reads only

## Current release reading

The current Phase 12 release-facing reading is:

- `drivers/net/virtio_net.c`: bounded Zig starter plus survey evidence are present through `Documentation/zigux/phase12-virtio-net-survey.md`, but public-read fallback still remains shared-tree-only rather than commit-pinned
- `drivers/nvme/host/pci.c`: bounded Zig starter, survey note, and slice note are present, and the archived packet also ships `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` for commit-pinned public fallback review
- `drivers/scsi/virtio_scsi.c`: bounded Zig starter, survey note, and slice note are present, and the lane also ships `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` as the current commit-pinned raw fallback catalog with a recorded bounded replay note
- `tools/lib/bpf/libbpf.c`: bounded segmented helper survey evidence is present through `Documentation/zigux/phase12-libbpf-segment-survey.md`, while the release packet now also keeps the focused libbpf-only replay shard explicit through `scripts/zigux/check-phase12-libbpf-focused-replay.py` and `zigux/tests/phase12_libbpf_only_build.zig`; public-read fallback still remains shared-tree-only rather than map-pinned or catalog-pinned
- `Documentation/zigux/README.md` now also mirrors the mixed fallback split directly, naming `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` as the dedicated commit-pinned fallback artifacts while `Documentation/zigux/phase12-virtio-net-survey.md` and `Documentation/zigux/phase12-libbpf-segment-survey.md` remain shared-tree-only fallback reads
- the shared replay packet stays reviewable through `zigux/tests/phase12_build.zig`, `make -C zigux phase12-validate`, and `make -C zigux phase12`
- the compile-smoke packet now stays explicit for the approved non-native musl targets `x86_64-linux-musl`, `aarch64-linux-musl`, and `riscv64-linux-musl` instead of living only as implicit test wiring
- the raw-fallback packet now keeps the split explicit: two anchors have dedicated commit-pinned fallback artifacts, and two anchors still rely on shared-tree fallback reads

- `PHASE12_ROADMAP_ANCHOR_COUNT=4`
- `PHASE12_COMMIT_PINNED_RAW_FALLBACK_COUNT=2`
- `PHASE12_SHARED_TREE_ONLY_FALLBACK_COUNT=2`
- `PHASE12_APPROVED_CROSS_TARGET_COUNT=3`
- `PHASE12_RELEASE_CLOSED=no`

## Evidence set

The current bounded release-evidence set is:

- `Documentation/zigux/phase12-release-readiness-survey.md`
- `Documentation/zigux/phase12-cross-compile-smoke.md`
- `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
- `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`
- `Documentation/zigux/phase12-virtio-net-survey.md`
- `Documentation/zigux/phase12-nvme-pci-survey.md`
- `Documentation/zigux/phase12-nvme-pci-slice.md`
- `Documentation/zigux/phase12-virtio-scsi-survey.md`
- `Documentation/zigux/phase12-virtio-scsi-slice.md`
- `Documentation/zigux/phase12-libbpf-segment-survey.md`
- `scripts/zigux/check-phase12-cross.py`
- `scripts/zigux/check-phase12-libbpf-focused-replay.py`
- `scripts/zigux/check-phase12-libbpf-packet.py`
- `scripts/zigux/check-phase12-libbpf-snapshot.py`
- `scripts/zigux/validate-phase12.py`
- `zigux/tests/phase12_cross_build.zig`
- `zigux/tests/phase12_build.zig`
- `zigux/tests/phase12_libbpf_only_build.zig`
- `zigux/tests/phase12_libbpf_segments.zig`
- `zigux/tests/phase12_libbpf_reviewability.zig`
- `zigux/tests/phase12_nvme_pci.zig`
- `zigux/tests/phase12_virtio_scsi_survey.zig`
- `zigux/tests/fixtures/phase12_libbpf_snapshot.json`
- `zigux/tests/phase12_libbpf_manifest.json`
- `zigux/tests/phase12_virtio_scsi_manifest.json`
- `tools/lib/bpf/zigux_segments/manifest.json`
- `zigux/Makefile`

## Gates

1. validate the shared Phase 12 survey packet
- `python3 scripts/zigux/validate-phase12.py`

2. run the make-level validation entrypoint
- `make -C zigux phase12-validate`

3. replay the bounded cross-compile smoke packet
- `python3 scripts/zigux/check-phase12-cross.py --zig <zig-path>`

4. run the focused libbpf-only replay shard
- `python3 scripts/zigux/check-phase12-libbpf-focused-replay.py`
- `zig build test --build-file zigux/tests/phase12_libbpf_only_build.zig --summary all`

5. run the shared Phase 12 build replay
- `zig build test --build-file zigux/tests/phase12_build.zig --summary all`

6. run the Linux-style combined Phase 12 entrypoint
- `make -C zigux phase12`

## Non-goals

This survey does not claim:

- global Phase 12 closure
- full runtime parity for `virtio_net`, `nvme_pci`, or `virtio_scsi`
- DMA-backed queue ownership, full interrupt or transport lifecycle parity, or deeper probe or teardown flows beyond the current bounded starters
- libbpf object-model, loader, relocation, file-path-and-handle bridge, or perf-buffer-online-cpu-routing closure
- equivalent current-head raw fallback coverage for every Phase 12 anchor

## Next bounded step

If this PMO lane reopens, the next honest follow-up is to fail-close the shared Phase 12 validator and scripts index on this release-readiness survey itself, so `scripts/zigux/validate-phase12.py` and `scripts/zigux/README.md` must keep the mixed fallback split, the bounded cross-compile packet, and the active-not-closed PMO reading explicit instead of leaving this release-facing note easier to drift than the surrounding driver and fallback artifacts.