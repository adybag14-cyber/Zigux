# Phase 12 Virtio Net Survey

This note records the current-master verification result for the bounded Phase 12 lane around `drivers/net/virtio_net.c`.

## Status

- `PHASE12_STATUS=starter-present-post-reset-replay-followup`
- `PHASE12_SLICE=virtio-net-survey`
- lane owner: `P12-L02`
- scope: keep the bounded queue-topology, refill-order, control-queue, post-reset replay, queue-reset, and transmit-recycle review packet truthful without reopening live runtime data-path work
- verified head: `b53ec2bd507d0b3283486e76acc273b184ad5bf8`
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
- current `master` now also carries `drivers/net/virtio_net_queue_resume.zig`
- current `master` now also carries `drivers/net/virtio_net_transmit_recycle.zig`
- current `master` now also carries `drivers/net/virtio_net_post_reset_replay.zig`
- current `master` now carries `zigux/tests/phase12_virtio_net.zig`
- current `master` now carries `zigux/tests/phase12_virtio_net_queue_resume.zig`
- current `master` now carries `zigux/tests/phase12_virtio_net_transmit_recycle.zig`
- current `master` now carries `zigux/tests/phase12_virtio_net_post_reset_replay.zig`
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
- `drivers/net/virtio_net_post_reset_replay.zig` keeps `summarizePostResetReplay()` reviewable so control-queue restore, receive-refill replay, transmit-recycle readiness, and probe-snapshot replay checkpoints stay explicit before queue resume without claiming runtime queue execution
- current `master` now carries `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, and `zigux/tests/phase12_virtio_net_syntax_lab.zig`, so the direct starter packet, queue-resume helper, transmit recycle helper, post-reset replay helper, and syntax-lab coverage all remain fail-closed on published head

## Truthful boundary

The truthful current boundary is still intentionally narrow:

- the bounded starter and its directly coupled tests are present on `master`
- the starter now includes the queue-resume, transmit-recycle, and post-reset replay follow-ups beside queue-topology, refill-order, control-queue recovery, control-queue payload shaping, and queue-reset recovery reviewability
- the shared Phase 12 build route includes the dedicated `virtio_net` syntax-lab smoke shard plus the direct queue-resume and transmit-recycle replays
- the packet still does not claim live DMA-safe receive ownership, page-pool wiring, refill execution, transport-backed submit flow, interrupt-backed completion handling, or full `net_device` lifecycle parity
- throughput and recovery parity remain roadmap requirements that need later bounded follow-ups before any broader complex-driver claim becomes honest

## Ownership and overlap

`P12-L02` owns one bounded complex-driver or segmented-helper step inside this queueing and throughput review packet.

That means this lane may:

1. restate the truthful current-master packet boundary
2. keep the bounded direct test, syntax lab, survey gate, and manifest packet aligned
3. land one more exact reviewability helper when it stays below runtime queue execution

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
