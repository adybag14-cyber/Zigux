# Phase 12 Virtio Net Survey

This note records the current-master verification result for the bounded Phase 12 lane around `drivers/net/virtio_net.c`.

## Status

- `PHASE12_STATUS=starter-present-transmit-recycle-followup`
- `PHASE12_SLICE=virtio-net-survey`
- lane owner: `P12-L04`
- scope: keep the bounded queue-topology, refill-order, control-queue, queue-reset, and transmit-recycle review packet truthful without reopening live runtime data-path work
- verified head: `bb423a0308879c18054c720bbccb67a3de3e0951`
- repo-truth boundary:
  - `Documentation/zigux/phase12-virtio-net-survey.md`
  - `zigux/tests/phase12_virtio_net_manifest.json`
  - `zigux/tests/phase12_virtio_net_survey.zig`
  - `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`
  - `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`

## Why this lane still matters

The Phase 12 roadmap still names `drivers/net/virtio_net.c` as a complex production-driver target.

That remains high-value because `virtio_net.c` spans probe-time negotiation, queue sizing, recovery sequencing, receive and transmit coordination, control-virtqueue state, RSS state, and full `net_device` lifecycle handling. The roadmap therefore still requires DMA-safe abstractions, queueing correctness, throughput and recovery parity, and segmented rollout before any honest live data-path claim.

## Current-master verification

- current `master` still carries the earlier Phase 10 virtio groundwork in `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, and `zigux/tests/phase10_build.zig`
- current `master` now carries `drivers/net/virtio_net.zig`
- current `master` now also carries `drivers/net/virtio_net_transmit_recycle.zig`
- current `master` now also carries `drivers/net/virtio_net_queue_resume.zig`
- current `master` now carries `zigux/tests/phase12_virtio_net.zig`
- current `master` now carries `zigux/tests/phase12_virtio_net_transmit_recycle.zig`
- current `master` now carries `zigux/tests/phase12_virtio_net_queue_resume.zig`
- current `master` now carries `zigux/tests/phase12_virtio_net_syntax_lab.zig`
- current `master` now carries `zigux/tests/phase12_virtio_net_survey.zig`
- current `master` now carries `zigux/tests/phase12_virtio_net_manifest.json`
- current `master` now carries `zigux/tests/phase12_build.zig`
- the shared Phase 12 smoke and test routes keep the dedicated `virtio_net` syntax-lab shard plus the queue-resume and transmit-recycle replays reachable beside the direct starter packet

Those checks mean the current lane is no longer a reland placeholder. The published packet now keeps a bounded Zig starter, direct test packet, dedicated syntax lab, dedicated survey gate, manifest, and shared Phase 12 build route on `master`, while still stopping below any live runtime DMA or transport-backed data-path claim.

## Packet boundary

The current bounded packet keeps the following reviewable without claiming runtime execution:

- `drivers/net/virtio_net.zig` keeps probe fallback, `summarizeQueueTopology()`, mergeable receive-buffer planning, `summarizeReceiveRefill()`, `controlQueueRecoveryPlan()`, `planControlQueuePayloadShape()`, `freezeForReset()`, `recoveryQueuePlan()`, and `restoreAfterReset()` explicit
- `drivers/net/virtio_net_queue_resume.zig` keeps the bounded queue-resume handoff reviewable so restore-time queue clamping and probe-snapshot refresh requirements stay visible without claiming runtime queue execution
- `drivers/net/virtio_net_transmit_recycle.zig` keeps `summarizeTransmitRecycle()` reviewable so transmit completion reuse, wake-threshold behavior, and stopped-versus-running queue disposition stay visible without claiming interrupt-backed completion handling
- current `master` now carries `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, and `zigux/tests/phase12_virtio_net_syntax_lab.zig`, so the direct starter packet, queue-resume helper, transmit recycle helper, and syntax-lab coverage all remain fail-closed on published head

## Truthful boundary

The truthful current boundary is still intentionally narrow:

- the bounded starter and its directly coupled tests are present on `master`
- the starter now includes the queue-resume and transmit-recycle follow-ups beside queue-topology, refill-order, control-queue recovery, control-queue payload shaping, and queue-reset recovery reviewability
- the shared Phase 12 build route includes the dedicated `virtio_net` syntax-lab smoke shard plus the direct queue-resume and transmit-recycle replays
- the packet still does not claim live DMA-safe receive ownership, page-pool wiring, refill execution, transport-backed submit flow, interrupt-backed completion handling, or full `net_device` lifecycle parity
- throughput and recovery parity remain roadmap requirements that need later bounded follow-ups before any broader complex-driver claim becomes honest

## Ownership and overlap

`P12-L04` owns only stale packet-local scaffold cleanup, perf-drift wording cleanup, and risk-note truthfulness for this bounded queueing and throughput review packet.

That means this lane may:

1. restate the truthful current-master packet boundary
2. keep the bounded direct test, syntax lab, survey gate, and manifest packet aligned
3. close another exact reviewability refresh if one of those directly coupled surfaces drifts again

That also means this lane does not own broader runtime queue execution, DMA completion behavior, NAPI, XDP, XSK, control-virtqueue command traffic, RSS table programming, or full `net_device` lifecycle work.

## Non-goals

This note does not claim:

- live DMA-safe receive ownership
- runtime refill execution
- transport-backed receive or transmit submission
- interrupt-backed transmit completion handling
- NAPI, page-pool DMA, XDP, XSK, control-virtqueue command traffic, RSS table programming, or `net_device` lifecycle parity

## Next bounded step

If this lane reopens, keep the follow-through inside the same packet.

The next bounded step is:

1. reread `Documentation/zigux/phase12-virtio-net-survey.md`, `zigux/tests/phase12_virtio_net_manifest.json`, and `zigux/tests/phase12_virtio_net_survey.zig` together
2. fix only the next packet-local stale scaffold, perf-drift note, or exact reviewability refresh
3. leave queue-execution, throughput, and broader recovery expansion to their own later Phase 12 follow-up lanes
