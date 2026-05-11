# Phase 12 Virtio Net Survey

This note records the current-master verification result for the bounded Phase 12 lane around `drivers/net/virtio_net.c`.

## Status

- `PHASE12_STATUS=starter-present-validation-incomplete`
- `PHASE12_SLICE=virtio-net-queue-recovery-survey`
- scope: verify whether current `master` carries a bounded `virtio_net` Zig starter for queue recovery, receive refill, mergeable-buffer sizing, and transmit recycle, and whether dedicated Phase 12 gates exist beside it
- verified on: `2026-05-11`
- repo-truth boundary:
  - `drivers/net/virtio_net.zig`
  - `Documentation/zigux/phase12-virtio-net-survey.md`
  - `zigux/tests/phase12_virtio_net_manifest.json`
  - `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`
  - `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`
- public fallback posture: shared-tree-only anchor; unlike `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, this `virtio_net` note is still a shared-tree survey rather than a commit-pinned raw GitHub fallback artifact.

## Why this lane still matters

The Phase 12 roadmap still names `drivers/net/virtio_net.c` as a complex production-driver target.

That anchor is still high value because `virtio_net.c` is a large production driver with probe-time negotiation, virtqueue management, recovery decisions, receive and transmit coordination, control-virtqueue work, RSS state, and full `net_device` lifecycle handling. The roadmap therefore still requires DMA-safe abstractions, queueing correctness, throughput and recovery parity, and segmented rollout before any honest live data-path claim.

## Current-master verification

- current `master` still carries the earlier Phase 10 virtio groundwork in `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, and `zigux/tests/phase10_build.zig`
- current `master` now carries `drivers/net/virtio_net.zig`
- the live `virtio_net` Zig packet is a bounded planning surface rather than a data-path implementation: it exposes `freezeForRecovery`, `restoreAfterRecovery`, `planQueueResume`, `planReceiveRefill`, `planMergeableBufferLength`, and `planTransmitRecycle`
- `planQueueResume` now derives queue rebuild scope from the remembered recovery state, control-queue presence, and RSS recovery state, distinguishing data-only, data-plus-control, and data-plus-control-plus-RSS resume paths
- `planReceiveRefill` records whether mergeable receive buffers need extra headroom and whether a fresh post-restore probe replay is required before refill work is trusted again
- `planMergeableBufferLength` guards the bounded mergeable-buffer sizing path with page-size, tailroom, headroom, and cache-line alignment checks, including explicit `PageTooSmallForMergeableBuffer` failure cases
- `planTransmitRecycle` records whether transmit recycle must wait for control-queue restore, RSS reapply, and receive-refill coordination before queue reuse proceeds
- current `master` still does not carry `zigux/tests/phase12_build.zig`
- current `master` still does not carry `zigux/tests/phase12_virtio_net_survey.zig`
- current `master` still does not carry `zigux/tests/phase12_virtio_net_syntax_lab.zig`
- current `master` still carries `zigux/tests/phase12_virtio_net_manifest.json` as the survey manifest for this lane family
- `zigux/Makefile` still carries `phase12-smoke`, `phase12-test`, and `phase12` targets even though the shared Phase 12 build file is absent

Those checks mean the present lane is no longer fully parked: the live tree has a driver-local queue and recovery starter again. What is still missing is the runnable verification envelope beside it.

## Truthful boundary

The truthful current boundary is:

- the roadmap still wants a bounded `virtio_net` lane in Phase 12
- the Phase 10 virtio foundation still exists and remains the nearest reusable substrate
- current `master` now carries a bounded `drivers/net/virtio_net.zig` starter for queue recovery planning, receive refill planning, mergeable-buffer sizing, and transmit recycle ordering
- current `master` still lacks the Phase 12 build file and direct survey or syntax-lab shards needed to execute those queue and recovery claims as a dedicated gate
- throughput parity, post-restore replay validation, DMA-safe refill ownership, and live queue execution remain blocked beyond the current starter

## Non-goals

This note does not claim:

- a current runnable `phase12` build surface
- a current direct smoke shard for `virtio_net`
- live DMA-safe receive ownership or page-pool wiring
- live NAPI, XDP, XSK, control-virtqueue command traffic, RSS table programming, or `net_device` lifecycle parity
- a current throughput benchmark or measured recovery parity result

## Next bounded step

The next honest same-lane move is to restore the missing validation packet around the live starter rather than pretending the data path is ready.

The next bounded step is:

1. reland `zigux/tests/phase12_build.zig`
2. reland the matching direct survey or syntax-lab shard under `zigux/tests/phase12_virtio_net*.zig` so the current queue and recovery helpers can be exercised directly
3. rerun `python3 scripts/zigux/check-build-only-phase12-surface.py`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12` before making any stronger throughput or recovery-parity claim

Until that validation packet is relanded, treat the current starter as a useful queue and recovery planning surface, but not yet as a runnable throughput or live recovery proof.
