# Phase 12 Virtio Net Survey

This note records the current-master verification result for the bounded Phase 12 lane around `drivers/net/virtio_net.c`.

## Status

- `PHASE12_STATUS=starter-present-buffer-planner`
- `PHASE12_SLICE=virtio-net-mergeable-receive-buffer-starter`
- scope: verify the bounded `virtio_net` Zig starter around probe fallback and mergeable receive-buffer planning without widening into live DMA, NAPI, XDP, XSK, control-virtqueue runtime commands, RSS table programming, or full `net_device` lifecycle work
- verified on: `2026-05-12`
- repo-truth boundary:
  - `drivers/net/virtio_net.zig`
  - `zigux/tests/phase12_virtio_net.zig`
  - `zigux/tests/phase12_virtio_net_syntax_lab.zig`
  - `Documentation/zigux/phase12-virtio-net-survey.md`
  - `zigux/tests/phase12_virtio_net_manifest.json`
  - `zigux/tests/phase12_virtio_net_survey.zig`
  - `zigux/tests/phase12_build.zig`

## Why this lane still matters

The Phase 12 roadmap still names `drivers/net/virtio_net.c` as a complex production-driver target.

That anchor remains high value because `virtio_net.c` still covers probe-time negotiation, queue-pair topology, recovery decisions, receive and transmit coordination, control-virtqueue work, RSS state, and full `net_device` lifecycle handling. The roadmap therefore still requires DMA-safe abstractions, queueing correctness, throughput and recovery parity, and segmented rollout before any honest live data-path claim.

## Current-master verification

- current `master` still carries the earlier Phase 10 virtio groundwork in `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, and `zigux/tests/phase10_build.zig`
- current `master` now carries `drivers/net/virtio_net.zig`
- the current bounded starter exposes `captureProbeSnapshot()` for queue-pair fallback plus header-shape selection and `planMergeableReceiveBuffer()` for the probe-time packet-buffer choice
- current `master` now carries `zigux/tests/phase12_virtio_net.zig` as the direct starter replay for this bounded packet
- current `master` now carries `zigux/tests/phase12_virtio_net_syntax_lab.zig` as the dedicated syntax lab for this bounded packet
- current `master` still carries `zigux/tests/phase12_virtio_net_survey.zig` and `zigux/tests/phase12_virtio_net_manifest.json` as the survey-backed lane guard
- current `master` now carries `zigux/tests/phase12_build.zig`, and that shared build route now carries the direct `virtio_net` syntax-lab smoke shard alongside the shipped `virtio_scsi` packet
- `zigux/Makefile` still carries `phase12-smoke`, `phase12-test`, and `phase12`, and those shared routes now pick up the bounded `virtio_net` syntax-lab smoke shard through the shared Phase 12 build route

Those checks mean the current lane has moved forward from a survey-only absence boundary into a bounded driver-local starter, but it is still intentionally below any live runtime or DMA-backed data-path claim.

## Truthful boundary

The truthful current boundary is:

- the roadmap still wants a bounded `virtio_net` lane in Phase 12
- the Phase 10 virtio foundation still exists and remains the nearest reusable substrate
- current `master` now carries `drivers/net/virtio_net.zig`, but the current starter is still deliberately small and limited to probe fallback plus mergeable receive-buffer planning
- the bounded starter models packet-buffer choice through `planMergeableReceiveBuffer()` without claiming live DMA-safe receive ownership, page-pool wiring, refill execution, or transport-backed submit flow
- current `master` now carries `zigux/tests/phase12_virtio_net.zig` and `zigux/tests/phase12_virtio_net_syntax_lab.zig`, so the current starter is directly executable and syntax-checked through the shared Phase 12 smoke route
- current `master` still carries `zigux/tests/phase12_virtio_net_survey.zig`, so the survey-backed boundary continues to machine-check the starter-present packet and its blocked runtime claims
- current `master` still does not claim live DMA-safe receive ownership, NAPI, XDP, XSK, control-virtqueue runtime traffic, RSS table programming, throughput parity, or full `net_device` lifecycle coverage

## Non-goals

This note does not claim:

- a current live refill loop
- a current DMA-safe receive ownership path
- a current transport-backed queue execution path
- a current throughput benchmark or measured recovery parity result
- a current NAPI, XDP, XSK, RSS table programming, control-virtqueue command, or `net_device` lifecycle implementation

## Next bounded step

The next honest same-lane move is still a bounded probe-snapshot or queue-summary follow-up, not a runtime data-path jump.

The next bounded step is:

1. keep the current starter focused on probe-time fallback and packet-buffer choice instead of widening into live DMA or lifecycle code
2. reland one probe-snapshot or queue-summary follow-up beside the current starter so the next queue-facing contract is reviewable without overclaiming runtime behavior
3. revisit shared `phase12_build.zig` or `zigux/Makefile` wiring only after that follow-up exists and still fits the bounded starter packet

Until then, treat the current starter as a real but deliberately small Phase 12 packet-buffer step, not as a live runtime proof.
