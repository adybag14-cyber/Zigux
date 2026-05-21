# Phase 12 Virtio Net Survey

This note records the current-master verification result for the bounded Phase 12 lane around `drivers/net/virtio_net.c`.

## Status

- `PHASE12_STATUS=split-helper-packet-present-shared-build-quintet-throughput-review-only`
- `PHASE12_SLICE=virtio-net-survey`
- lane owner: `P12-L01`
- scope: keep the bounded queue-resume, receive-refill replay, transmit-recycle, post-reset replay, and throughput-parity review packet truthful without reopening live runtime data-path work
- verified head: `c36b21af252cf76160ba5ae9c8f84b2310f4b2e1`
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
- current `master` now carries `drivers/net/virtio_net_queue_resume.zig`
- current `master` now carries `drivers/net/virtio_net_receive_refill_replay.zig`
- current `master` now carries `drivers/net/virtio_net_transmit_recycle.zig`
- current `master` now carries `drivers/net/virtio_net_post_reset_replay.zig`
- current `master` now carries `drivers/net/virtio_net_throughput_parity.zig`
- current `master` now carries `zigux/tests/phase12_virtio_net_queue_resume.zig`
- current `master` now carries `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`
- current `master` now carries `zigux/tests/phase12_virtio_net_transmit_recycle.zig`
- current `master` now carries `zigux/tests/phase12_virtio_net_post_reset_replay.zig`
- current `master` now carries `zigux/tests/phase12_virtio_net_throughput_parity.zig`
- current `master` now carries `zigux/tests/phase12_virtio_net_survey.zig`
- current `master` now carries `zigux/tests/phase12_virtio_net_manifest.json`
- current `master` now carries `zigux/tests/phase12_build.zig`
- current `master` does not carry the older monolithic `drivers/net/virtio_net.zig` starter or the dedicated `zigux/tests/phase12_virtio_net_syntax_lab.zig` shard anymore
- `zigux/tests/phase12_build.zig` now keeps the dedicated `virtio_net_queue_resume`, `virtio_net_receive_refill_replay`, `virtio_net_transmit_recycle`, `virtio_net_post_reset_replay`, and `virtio_net_throughput_parity` replays reachable through the shared Phase 12 smoke and test routes; `zigux/Makefile` still exposes `phase12-smoke`, `phase12-test`, and `phase12` convenience entrypoints

Those checks mean the current lane is no longer a reland placeholder. The published packet now keeps a bounded split-helper review surface, directly coupled tests, dedicated survey gate, manifest, returned shared make entrypoints, and a shared Phase 12 build route on `master`, while still stopping below any live runtime DMA or transport-backed data-path claim.

## Packet boundary

The current bounded packet keeps the following reviewable without claiming runtime execution:

- `drivers/net/virtio_net_queue_resume.zig` keeps the bounded queue-resume handoff reviewable so restore-time queue clamping, refill replay, transmit recycle, and probe-snapshot refresh requirements stay visible without claiming runtime queue execution
- `drivers/net/virtio_net_receive_refill_replay.zig` keeps `summarizeReceiveRefillReplay()` reviewable so control-queue restore, receive-queue-pair preservation, refill-budget restoration, and descriptor repost requirements stay explicit before queue submission resumes without claiming runtime descriptor posting
- `drivers/net/virtio_net_transmit_recycle.zig` keeps `summarizeTransmitRecycle()` reviewable so transmit completion reuse, wake-threshold behavior, and stopped-versus-running queue disposition stay visible without claiming interrupt-backed completion handling
- `drivers/net/virtio_net_post_reset_replay.zig` keeps `summarizePostResetReplay()` reviewable so control-queue restore, receive-refill replay, transmit-recycle readiness, and probe-snapshot replay checkpoints stay explicit before queue resume without claiming runtime queue execution
- `drivers/net/virtio_net_throughput_parity.zig` keeps `summarizeThroughputParity()` reviewable so queue-pair restore, refill-budget preservation, transmit-recycle readiness, and post-reset replay checkpoints stay visible as review-only throughput-ratio checks without claiming live transport execution
- current `master` now carries `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, and `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and the shared Phase 12 build route reruns that quintet so the split helper packet remains fail-closed on published head

## Truthful boundary

The truthful current boundary is still intentionally narrow:

- the split helper packet and its directly coupled tests are present on `master`
- the packet now exposes queue resume, receive-refill replay, transmit recycle, post-reset replay, and throughput-parity reviewability without reviving the older monolithic starter scaffold
- the shared Phase 12 build route includes the queue-resume, receive-refill replay, transmit-recycle, post-reset replay, and throughput-parity replays, and current `zigux/Makefile` still exposes `phase12-smoke`, `phase12-test`, and `phase12`
- the throughput-parity helper is still a review-only throughput-ratio summary, not measured transport throughput evidence
- the packet still does not claim live DMA-safe receive ownership, page-pool wiring, refill execution, transport-backed submit flow, interrupt-backed completion handling, or full `net_device` lifecycle parity
- throughput and recovery parity remain roadmap requirements that need later bounded follow-ups before any broader complex-driver claim becomes honest

## Ownership and overlap

`P12-L01` owns one bounded stale-scaffold, survey-gate, or performance-risk note cleanup step inside this queueing and throughput review packet.

That means this lane may:

1. restate the truthful current-master packet boundary
2. keep the bounded direct test, survey gate, and manifest packet aligned
3. fix one packet-local stale scaffold, expected-output drift, exact reviewability refresh, or performance-risk wording refresh when it stays below runtime queue execution

That also means this lane does not own broader runtime queue execution, DMA completion behavior, NAPI, XDP, XSK, control-virtqueue command traffic, RSS table programming, or full `net_device` lifecycle work.

## Non-goals

This note does not claim:

- live DMA-safe receive ownership
- runtime refill execution
- transport-backed receive or transmit submission
- interrupt-backed transmit completion handling
- measured transport throughput evidence
- NAPI, page-pool DMA, XDP, XSK, control-virtqueue command traffic, RSS table programming, or `net_device` lifecycle parity

## Next bounded step

If this lane reopens, keep the follow-through inside the same packet.

The next bounded step is:

1. reread `Documentation/zigux/phase12-virtio-net-survey.md`, `zigux/tests/phase12_virtio_net_manifest.json`, and `zigux/tests/phase12_virtio_net_survey.zig` together
2. fix only the next packet-local stale scaffold, shared-route wording drift, exact reviewability refresh, or performance-risk wording refresh
3. leave queue-execution, throughput, and broader recovery expansion to their own later Phase 12 follow-up lanes