# Phase 12 Virtio Net Survey

This document records the first bounded Phase 12 survey lane around `drivers/net/virtio_net.c`.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_SLICE=virtio-net-survey`
- scope: survey manifest, dedicated survey gate, shared Phase 12 build wiring, and a lane note that compares the live repo state against the roadmap for `drivers/net/virtio_net.zig`
- product boundary:
  - `zigux/tests/phase12_virtio_net_manifest.json`
  - `zigux/tests/phase12_virtio_net_survey.zig`
  - `zigux/tests/phase12_build.zig`
  - `Documentation/zigux/phase12-virtio-net-survey.md`

## Why this slice exists

The Phase 12 roadmap explicitly names `drivers/net/virtio_net.c` as a complex production-driver target, but the live repo still has no `drivers/net/virtio_net.zig` starter and no Phase 12 harness at all.

That matters because `virtio_net.c` is not a small leaf helper. The live file is 7,288 lines and mixes probe-time feature negotiation, receive and transmit virtqueue management, NAPI poll loops, XDP and XSK fast paths, page-pool and DMA handling, control-virtqueue commands, RSS and multiqueue configuration, ethtool hooks, and full `net_device` lifecycle work.

The highest-value honest step in this lane is therefore a survey checkpoint, not a premature driver scaffold.

## Survey findings

- `drivers/net/virtio_net.c` is present on `master` and is much larger than the earlier Phase 10 and Phase 11 starter anchors, which makes a direct first-pass Zig port a poor fit for the roadmap's bounded-delivery rule.
- the live repo does already ship the Phase 10 virtio groundwork in `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, and the matching `zigux/tests/phase10_build.zig` path.
- that Phase 10 footing is useful, but it still stops at in-memory queue and device bookkeeping. It does not cover the DMA-safe abstractions, queueing correctness, recovery behavior, or segmented rollout controls that the roadmap requires before real virtio_net data-path work can land honestly.
- the live repo still has no `drivers/net/virtio_net.zig`, no dedicated Phase 12 build file, no `make -C zigux phase12` target, and no Phase 12 survey note before this slice.
- the next honest driver-facing step is one tiny probe snapshot helper around negotiated feature bits, queue-pair counts, control-virtqueue presence, mergeable-buffer mode, and RSS or hash-report capability detection from `virtnet_probe()`.

## Recorded gaps

The survey manifest now records:

- the landed `phase12-build-gate`
- the landed `phase12-make-target`
- the landed `phase12-virtio-core-foundation`
- the landed `phase12-virtio-ring-foundation`
- the landed `phase12-virtio-net-survey-gate`
- the landed `phase12-virtio-net-survey-note`
- the ready-next `phase12-virtio-net-probe-snapshot-starter`
- the still-blocked `phase12-virtio-net-runtime-data-path`

This keeps the lane explicit without overstating progress: Zigux now has a reviewable Phase 12 checkpoint, but it does not yet claim any net-driver implementation.

## Non-goals

This survey slice does not claim:

- a `drivers/net/virtio_net.zig` starter
- NAPI poll behavior
- page-pool or DMA-backed buffer management
- XDP or XSK fast paths
- control-virtqueue command helpers
- RSS table programming, ethtool hooks, or channel reconfiguration
- `net_device` registration, open or close flows, suspend or resume, or teardown parity

## Gates

1. run the dedicated Phase 12 build
- `zig build test --build-file zigux/tests/phase12_build.zig`

2. run the convenience target
- `make -C zigux phase12`

## Next bounded step

Stay in the Phase 12 virtio_net lane and add one tiny `drivers/net/virtio_net.zig` probe snapshot helper next so the lane can describe the feature and queue-plan branch of `virtnet_probe()` before any NAPI, XDP, DMA, control-virtqueue, or `net_device` lifecycle work.
