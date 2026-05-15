# Phase 12 Virtio Net Survey

This note records the current-master verification result for the bounded Phase 12 lane around `drivers/net/virtio_net.c`.

## Status

- `PHASE12_STATUS=starter-present-transmit-recycle-followup`
- `PHASE12_SLICE=virtio-net-transmit-recycle-followup`
- `PHASE12_LANE=P12-L04`
- scope: verify the bounded `virtio_net` Zig starter around probe fallback, queue-topology summary, mergeable receive-buffer planning, receive-refill summary, control-queue recovery sequencing, control-queue payload shaping, queue-reset recovery planning, queue-resume gating, and transmit-recycle disposition reviewability without widening into live DMA, NAPI, XDP, XSK, control-virtqueue runtime commands, RSS table programming, or full `net_device` lifecycle work
- verified on: `2026-05-15`
- inspected head: `bb423a0308879c18054c720bbccb67a3de3e0951`
- repo-truth boundary:
  - `drivers/net/virtio_net.zig`
  - `drivers/net/virtio_net_queue_resume.zig`
  - `drivers/net/virtio_net_transmit_recycle.zig`
  - `zigux/tests/phase12_virtio_net.zig`
  - `zigux/tests/phase12_virtio_net_queue_resume.zig`
  - `zigux/tests/phase12_virtio_net_transmit_recycle.zig`
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
- current `master` now also carries `drivers/net/virtio_net_queue_resume.zig`
- current `master` now also carries `drivers/net/virtio_net_transmit_recycle.zig`
- the current bounded starter exposes `captureProbeSnapshot()` for queue-pair fallback plus header-shape selection, `summarizeQueueTopology()` for receive, transmit, and optional control-virtqueue placement, `planMergeableReceiveBuffer()` for the probe-time packet-buffer choice, `summarizeReceiveRefill()` for room-reuse versus single-page versus mergeable-chain posting order, `controlQueueRecoveryPlan()` for restore ordering plus bounded receive-mode, hash-report, MAC, VLAN, and RSS resync planning, `planControlQueuePayloadShape()` for bounded control-queue payload sizing, and `freezeForReset()`, `recoveryQueuePlan()`, plus `restoreAfterReset()` for bounded queue-reset recovery planning
- the current bounded queue-resume follow-up now also exposes `summarizeQueueResume()` in `drivers/net/virtio_net_queue_resume.zig`, keeping post-reset resume checkpoints, refill-versus-control restore scope, fresh probe replay requirements, and throughput guard state reviewable without claiming live queue restart
- the current bounded follow-up now also exposes `summarizeTransmitRecycle()` in `drivers/net/virtio_net_transmit_recycle.zig`, keeping completed-descriptor freeing, wake-threshold checks, and stopped-versus-running transmit-queue disposition reviewable without claiming interrupt-backed completion handling
- current `master` now carries `zigux/tests/phase12_virtio_net.zig` as the direct starter replay for this bounded packet
- current `master` now carries `zigux/tests/phase12_virtio_net_queue_resume.zig` as the direct replay for the bounded queue-resume follow-up
- current `master` now carries `zigux/tests/phase12_virtio_net_transmit_recycle.zig` as the direct replay for the bounded transmit-recycle follow-up
- current `master` now carries `zigux/tests/phase12_virtio_net_syntax_lab.zig` as the dedicated syntax lab for this bounded packet
- current `master` still carries `zigux/tests/phase12_virtio_net_survey.zig` and `zigux/tests/phase12_virtio_net_manifest.json` as the survey-backed lane guard
- current `master` now carries `zigux/tests/phase12_build.zig`, and that shared build route now carries the direct `virtio_net` syntax-lab smoke shard plus the dedicated `virtio_net_queue_resume` and `virtio_net_transmit_recycle` replays alongside the shipped `virtio_scsi` packet
- `zigux/Makefile` still carries `phase12-smoke`, `phase12-test`, and `phase12`, and those shared routes now pick up the bounded `virtio_net` syntax-lab smoke shard plus the direct queue-resume and transmit-recycle replays through the shared Phase 12 build route

Those checks mean the current lane has moved forward from a control-queue payload-shaping packet into a bounded queue-resume plus transmit-recycle follow-up, but it is still intentionally below any live runtime or DMA-backed data-path claim.

## Truthful boundary

The truthful current boundary is:

- the roadmap still wants a bounded `virtio_net` lane in Phase 12
- the Phase 10 virtio foundation still exists and remains the nearest reusable substrate
- current `master` now carries `drivers/net/virtio_net.zig`, and the current starter now covers probe fallback, queue-topology summary, mergeable receive-buffer planning, receive-refill summary, control-queue recovery sequencing, control-queue payload shaping, and queue-reset recovery planning
- current `master` now also carries `drivers/net/virtio_net_queue_resume.zig`, and the bounded follow-up keeps post-reset resume checkpoints, refill-versus-control restore scope, fresh probe replay requirements, and throughput guard state reviewable without claiming live queue restart
- current `master` now also carries `drivers/net/virtio_net_transmit_recycle.zig`, and the bounded follow-up keeps completed-descriptor freeing, wake-threshold checks, and stopped-versus-running queue disposition reviewable without claiming live transmit completion handling
- the bounded queue-topology follow-up keeps receive and transmit pair counts plus optional control-virtqueue placement reviewable without claiming live queue execution
- the bounded starter models packet-buffer choice through `planMergeableReceiveBuffer()`, keeps posting order reviewable through `summarizeReceiveRefill()`, keeps control-queue restore ordering reviewable through `controlQueueRecoveryPlan()`, keeps control-queue payload boundaries reviewable through `planControlQueuePayloadShape()`, keeps reset sequencing reviewable through `freezeForReset()`, `recoveryQueuePlan()`, and `restoreAfterReset()`, now keeps transmit recycle disposition reviewable through `summarizeTransmitRecycle()`, and now keeps queue-resume recovery gates reviewable through `summarizeQueueResume()` without claiming live DMA-safe receive ownership, page-pool wiring, refill execution, or transport-backed submit flow
- current `master` now carries `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, and `zigux/tests/phase12_virtio_net_syntax_lab.zig`, so the current starter plus queue-resume and transmit-recycle follow-ups are directly executable and syntax-checked through the shared Phase 12 smoke and test routes
- current `master` still carries `zigux/tests/phase12_virtio_net_survey.zig`, so the survey-backed boundary continues to machine-check the starter-present packet and its blocked runtime claims
- current `master` still does not claim live DMA-safe receive ownership, NAPI, XDP, XSK, control-virtqueue runtime traffic, RSS table programming, throughput parity, or full `net_device` lifecycle coverage

## Non-goals

This note does not claim:

- a current live refill loop
- a current DMA-safe receive ownership path
- a current transport-backed queue execution path
- a current throughput benchmark or measured recovery parity result
- a current transmit-completion interrupt or napi-driven recycle path
- a current NAPI, XDP, XSK, RSS table programming, control-virtqueue command, or `net_device` lifecycle implementation

## Next bounded step

The next honest same-lane move is now an exact reviewability refresh if this packet drifts again, not a runtime data-path jump.

The next bounded step is:

1. keep the current starter focused on probe fallback, queue-topology summary, packet-buffer choice, refill-order reviewability, control-queue recovery sequencing, control-queue payload shaping, queue-reset recovery planning, queue-resume gating, and transmit-recycle disposition reviewability instead of widening into live DMA or lifecycle code
2. revisit the direct test, queue-resume replay, transmit-recycle replay, syntax lab, manifest, survey gate, or this note only if another exact reviewability refresh becomes necessary inside the same packet
3. treat runtime queue execution, throughput parity, and DMA-safe ownership as blocked until later roadmap-backed abstractions land elsewhere

Until then, treat the current starter as a real but deliberately small Phase 12 queue-resume and transmit-recycle follow-up step, not as a live runtime proof.
