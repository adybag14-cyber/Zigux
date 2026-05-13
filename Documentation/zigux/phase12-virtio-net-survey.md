# Phase 12 Virtio Net Survey

This note records the current-master verification result for the bounded Phase 12 lane around `drivers/net/virtio_net.c`.

## Status

- `PHASE12_STATUS=starter-present-control-queue-payload-shaping`
- `PHASE12_SLICE=virtio-net-control-queue-payload-shaping-followup`
- scope: verify the bounded `virtio_net` Zig starter around probe fallback, queue-topology summary, mergeable receive-buffer planning, receive-refill summary, control-queue recovery sequencing, control-queue payload shaping, and queue-reset recovery planning without widening into live DMA, NAPI, XDP, XSK, control-virtqueue runtime commands, RSS table programming, or full `net_device` lifecycle work
- verified on: `2026-05-13`
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
- the current bounded starter exposes `captureProbeSnapshot()` for queue-pair fallback plus header-shape selection, `summarizeQueueTopology()` for receive, transmit, and optional control-virtqueue placement, `planMergeableReceiveBuffer()` for the probe-time packet-buffer choice, `summarizeReceiveRefill()` for room-reuse versus single-page versus mergeable-chain posting order, `controlQueueRecoveryPlan()` for restore ordering plus bounded receive-mode, hash-report, MAC, VLAN, and RSS resync planning, `planControlQueuePayloadShape()` for bounded control-queue payload sizing, and `freezeForReset()`, `recoveryQueuePlan()`, plus `restoreAfterReset()` for bounded queue-reset recovery planning
- current `master` now carries `zigux/tests/phase12_virtio_net.zig` as the direct starter replay for this bounded packet
- current `master` now carries `zigux/tests/phase12_virtio_net_syntax_lab.zig` as the dedicated syntax lab for this bounded packet
- current `master` still carries `zigux/tests/phase12_virtio_net_survey.zig` and `zigux/tests/phase12_virtio_net_manifest.json` as the survey-backed lane guard
- current `master` now carries `zigux/tests/phase12_build.zig`, and that shared build route now carries the direct `virtio_net` syntax-lab smoke shard alongside the shipped `virtio_scsi` packet
- `zigux/Makefile` still carries `phase12-smoke`, `phase12-test`, and `phase12`, and those shared routes now pick up the bounded `virtio_net` syntax-lab smoke shard through the shared Phase 12 build route

Those checks mean the current lane has moved forward from a control-queue recovery packet into a bounded control-queue payload-shaping follow-up, but it is still intentionally below any live runtime or DMA-backed data-path claim.

## Truthful boundary

The truthful current boundary is:

- the roadmap still wants a bounded `virtio_net` lane in Phase 12
- the Phase 10 virtio foundation still exists and remains the nearest reusable substrate
- current `master` now carries `drivers/net/virtio_net.zig`, and the current starter now covers probe fallback, queue-topology summary, mergeable receive-buffer planning, receive-refill summary, control-queue recovery sequencing, control-queue payload shaping, and queue-reset recovery planning
- the bounded queue-topology follow-up keeps receive and transmit pair counts plus optional control-virtqueue placement reviewable without claiming live queue execution
- the bounded starter models packet-buffer choice through `planMergeableReceiveBuffer()`, keeps posting order reviewable through `summarizeReceiveRefill()`, keeps control-queue restore ordering reviewable through `controlQueueRecoveryPlan()`, keeps control-queue payload boundaries reviewable through `planControlQueuePayloadShape()`, and keeps reset sequencing reviewable through `freezeForReset()`, `recoveryQueuePlan()`, and `restoreAfterReset()` without claiming live DMA-safe receive ownership, page-pool wiring, refill execution, or transport-backed submit flow
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

The next honest same-lane move is now an exact reviewability refresh if this packet drifts again, not a runtime data-path jump.

The next bounded step is:

1. keep the current starter focused on probe fallback, queue-topology summary, packet-buffer choice, refill-order reviewability, control-queue recovery sequencing, control-queue payload shaping, and queue-reset recovery planning instead of widening into live DMA or lifecycle code
2. revisit the direct test, syntax lab, manifest, survey gate, or this note only if another exact reviewability refresh becomes necessary inside the same packet
3. treat runtime queue execution, throughput parity, and DMA-safe ownership as blocked until later roadmap-backed abstractions land elsewhere

Until then, treat the current starter as a real but deliberately small Phase 12 control-queue-payload-shaping step, not as a live runtime proof.
