# Phase 12 Virtio Net Survey

This document records the bounded Phase 12 survey lane around `drivers/net/virtio_net.c`, the landed Zigux probe starter tied to it, and the already-landed queue-recovery and `hdr_len` follow-ups that keep this lane reviewable without widening into runtime data-path work.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_SLICE=virtio-net-survey`
- scope: survey manifest, dedicated survey gate, shared Phase 12 build wiring, the landed `drivers/net/virtio_net.zig` probe snapshot and `hdr_len` helpers, and a lane note that compares the live repo state against the roadmap for the broader driver
- product boundary:
  - `zigux/tests/phase12_virtio_net_manifest.json`
  - `zigux/tests/phase12_virtio_net_survey.zig`
  - `zigux/tests/phase12_virtio_net.zig`
  - `zigux/tests/phase12_build.zig`
  - `Documentation/zigux/phase12-virtio-net-survey.md`

## Why this slice exists

The Phase 12 roadmap explicitly names `drivers/net/virtio_net.c` as a complex production-driver target, and the live repo now carries only a tiny probe-time `drivers/net/virtio_net.zig` slice for that lane.

That still matters because `virtio_net.c` is not a small leaf helper. The live file is 7,288 lines and mixes probe-time feature negotiation, receive and transmit virtqueue management, NAPI poll loops, XDP and XSK fast paths, page-pool and DMA handling, control-virtqueue commands, RSS and multiqueue configuration, ethtool hooks, and full `net_device` lifecycle work.

The highest-value honest step in this lane is therefore a very small probe snapshot helper plus a matching `hdr_len` branch summary with bounded build wiring and risk notes, not a premature runtime data-path or net-device scaffold.

## Survey findings

- `drivers/net/virtio_net.c` is present on `master` and is much larger than the earlier Phase 10 and Phase 11 starter anchors, which makes a direct first-pass Zig port a poor fit for the roadmap's bounded-delivery rule.
- the live repo already ships the Phase 10 virtio groundwork in `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, and the matching `zigux/tests/phase10_build.zig` path.
- that Phase 10 footing now reaches core-side status sequencing, feature negotiation, queue callback bookkeeping, descriptor-shape metadata, notification accounting, ring-local queue-shape and notification bookkeeping, and input-side queue planning. It still does not cover the DMA-safe abstractions, queueing correctness, recovery behavior, or segmented rollout controls that the roadmap requires before real virtio_net data-path work can land honestly.
- this checkpoint has now been re-verified against current `master` head `2dbd78146b65f0e8a0e9c2dcda046d3041780ae8`, with the same probe snapshot, queue-recovery, and `hdr_len` helpers still defining the live bounded footing.
- the Phase 12 lane now consists of a dedicated build file, `make -C zigux phase12`, the survey gate, this note, `drivers/net/virtio_net.zig`, and a focused direct test for the new starter. The shared Phase 12 build should run both the survey gate and the direct probe-starter gate so stale build wiring cannot quietly park the driver slice.
- the landed starter records one bounded queueing and recovery-facing step from `virtnet_probe()`: negotiated feature counts, queue-pair fallback, control-virtqueue presence, mergeable-buffer mode, an explicit RSS outcome summary that distinguishes active, downgraded, hash-report-only, and unavailable states, and whether probe should treat the device as stable, renegotiate features, or reset-required.
- the lane now also lands one small queue-recovery follow-up: the probe snapshot records an explicit queue recovery action that distinguishes staying in bounded single-queue fallback, renegotiating features, and requiring reset when the control-virtqueue path or negotiated feature set cannot support the requested topology.
- the lane now also lands one tiny header-shape follow-up: the probe snapshot mirrors the `hdr_len` branch in `virtnet_probe()` so reviewability now distinguishes legacy headers, mergeable-or-version1 headers, hash-report headers, and UDP-tunnel headers without claiming any live queue activation or packet-path behavior.
- the lane now also lands one bounded queue-recovery summary follow-up: the lab can freeze the last in-memory queue topology and recovery posture, refuse fresh probe snapshots while recovery is in flight, and clear stale planning state after restore while preserving the remembered queue-pair count, total queue count, control-queue placement, RSS summary, and reset or renegotiation intent.

## Recorded gaps

The survey manifest now records:

- the landed `phase12-build-gate`
- the landed `phase12-make-target`
- the landed `phase12-virtio-core-foundation`
- the landed `phase12-virtio-ring-foundation`
- the landed `phase12-virtio-net-survey-gate`
- the landed `phase12-virtio-net-survey-note`
- the landed `phase12-virtio-net-probe-snapshot-starter`
- the landed `phase12-virtio-net-queue-recovery-followup`
- the landed `phase12-virtio-net-hdr-len-followup`
- the landed `phase12-virtio-net-queue-recovery-summary`
- the still-blocked `phase12-virtio-net-runtime-data-path`

This keeps the lane explicit without overstating progress: Zigux now has a reviewable Phase 12 probe snapshot starter plus the bounded queue-recovery summary follow-up and the newer header-shape follow-up, but it still does not claim DMA-backed queue setup, NAPI, control-virtqueue commands, or a usable net-driver lifecycle.

## Non-goals

This survey slice does not claim:

- NAPI poll behavior
- page-pool or DMA-backed buffer management
- XDP or XSK fast paths
- control-virtqueue command helpers beyond presence or fallback reporting
- RSS table programming, ethtool hooks, or channel reconfiguration
- `net_device` registration, open or close flows, suspend or resume, or teardown parity

## Gates

1. run the dedicated Phase 12 build
- `zig build test --build-file zigux/tests/phase12_build.zig`

2. run the convenience target
- `make -C zigux phase12`

## Next bounded step

Keep this lane on another probe-only capability handoff, most likely a tiny receive-buffer or header-scatter constraint summary, until the roadmap-approved DMA and queueing substrate exists for a truthful follow-up beyond the current probe snapshot, queue-recovery summary, and `hdr_len` helper.
