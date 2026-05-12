# Phase 12 Virtio Net Survey

This note records the current-master verification result for the bounded Phase 12 lane around `drivers/net/virtio_net.c`.

## Status

- `PHASE12_STATUS=survey-only-driver-absent`
- `PHASE12_SLICE=virtio-net-queue-recovery-survey`
- scope: verify whether current `master` still carries a bounded `virtio_net` Zig starter beside the dedicated Phase 12 survey gate and the shared smoke-first Phase 12 packet
- verified on: `2026-05-12`
- repo-truth boundary:
  - `Documentation/zigux/phase12-virtio-net-survey.md`
  - `zigux/tests/phase12_virtio_net_manifest.json`
  - `zigux/tests/phase12_virtio_net_survey.zig`
  - `zigux/tests/phase12_build.zig`
  - `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`
  - `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`
- public fallback posture: shared-tree-only anchor; unlike `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, this `virtio_net` note is still a shared-tree survey rather than a commit-pinned raw GitHub fallback artifact.

## Why this lane still matters

The Phase 12 roadmap still names `drivers/net/virtio_net.c` as a complex production-driver target.

That anchor is still high value because `virtio_net.c` is a large production driver with probe-time negotiation, virtqueue management, recovery decisions, receive and transmit coordination, control-virtqueue work, RSS state, and full `net_device` lifecycle handling. The roadmap therefore still requires DMA-safe abstractions, queueing correctness, throughput and recovery parity, and segmented rollout before any honest live data-path claim.

## Current-master verification

- current `master` still carries the earlier Phase 10 virtio groundwork in `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, and `zigux/tests/phase10_build.zig`
- current `master` does not carry `drivers/net/virtio_net.zig`
- current `master` still carries `zigux/tests/phase12_virtio_net_survey.zig` as the dedicated survey gate for this bounded lane reminder
- current `master` still carries `zigux/tests/phase12_virtio_net_manifest.json` as the survey manifest for this lane family
- current `master` now carries `zigux/tests/phase12_build.zig`, but that shared build route still wires only the shipped `virtio_scsi` smoke-first packet rather than a direct `virtio_net` replay
- current `master` still does not carry `zigux/tests/phase12_virtio_net_syntax_lab.zig`
- `zigux/Makefile` still carries `phase12-smoke`, `phase12-test`, and `phase12` targets, and those shared routes line up with `zigux/tests/phase12_build.zig` for the shipped `virtio_scsi` packet without yet promoting direct `virtio_net` validation

Those checks mean the present lane is parked on a survey-only boundary again: the shared Phase 12 smoke-first route is present for the shipped `virtio_scsi` tranche, the dedicated `virtio_net` survey packet still exists, but the driver-local Zig starter itself is absent from current `master` and the direct syntax-lab shard is still missing beside it.

## Truthful boundary

The truthful current boundary is:

- the roadmap still wants a bounded `virtio_net` lane in Phase 12
- the Phase 10 virtio foundation still exists and remains the nearest reusable substrate
- current `master` no longer reads back `drivers/net/virtio_net.zig`, so the queue-recovery starter is not presently a shipped driver-local surface
- current `master` still carries `zigux/tests/phase12_virtio_net_survey.zig`, so the survey-only and driver-absent boundary is executable as a direct survey gate
- current `master` now carries `zigux/tests/phase12_build.zig`, but that shared route still only proves the shipped `virtio_scsi` smoke-first packet rather than a direct `virtio_net` replay
- current `master` still lacks the direct syntax-lab shard and full direct replay needed to execute queue or recovery claims as a `virtio_net` smoke route
- throughput parity, post-restore replay validation, DMA-safe refill ownership, and live queue execution remain blocked beyond the current survey-only boundary

## Non-goals

This note does not claim:

- a current direct smoke shard for `virtio_net`
- a current driver-backed syntax lab
- a current `drivers/net/virtio_net.zig` starter on `master`
- live DMA-safe receive ownership or page-pool wiring
- live NAPI, XDP, XSK, control-virtqueue command traffic, RSS table programming, or `net_device` lifecycle parity
- a current throughput benchmark or measured recovery parity result

## Next bounded step

The next honest same-lane move is to reland the missing driver-local starter and its direct validation packet rather than pretending the data path is ready.

The next bounded step is:

1. keep `zigux/tests/phase12_build.zig` explicit as the shipped shared `virtio_scsi` smoke-first route rather than treating it as proof of direct `virtio_net` validation
2. reland the driver-local starter under `drivers/net/virtio_net.zig` together with the matching direct syntax-lab shard under `zigux/tests/phase12_virtio_net_syntax_lab.zig`, while keeping `zigux/tests/phase12_virtio_net_survey.zig` and `zigux/tests/phase12_virtio_net_manifest.json` aligned with the survey-only boundary until those files truly return
3. rerun `python3 scripts/zigux/check-build-only-phase12-surface.py`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12` before making any stronger throughput or recovery-parity claim

Until that driver-local packet is relanded, treat the current survey reminder as a useful Phase 12 absence boundary, but not as a runnable throughput or live recovery proof.
