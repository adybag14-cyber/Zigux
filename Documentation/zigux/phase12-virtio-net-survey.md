# Phase 12 Virtio Net Survey

This document records the bounded Phase 12 survey lane around `drivers/net/virtio_net.c`, the landed Zigux probe starter tied to it, and the already-landed queue-recovery, queue-resume, `hdr_len`, and receive-path follow-ups that keep this lane reviewable without widening into runtime data-path work.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_SLICE=virtio-net-survey`
- scope: survey manifest, dedicated survey gate, shared Phase 12 build wiring, the landed `drivers/net/virtio_net.zig` probe snapshot plus queue-recovery, queue-resume, `hdr_len`, and receive-path helpers, and a lane note that compares the live repo state against the roadmap for the broader driver
- product boundary:
  - `zigux/tests/phase12_virtio_net_manifest.json`
  - `zigux/tests/phase12_virtio_net_survey.zig`
  - `zigux/tests/phase12_virtio_net.zig`
  - `zigux/tests/phase12_build.zig`
  - `Documentation/zigux/phase12-virtio-net-survey.md`

## Why this slice exists

The Phase 12 roadmap explicitly names `drivers/net/virtio_net.c` as a complex production-driver target, and the live repo now carries only a tiny probe-time `drivers/net/virtio_net.zig` slice for that lane.

That still matters because `virtio_net.c` is not a small leaf helper. The live file is 7,288 lines and mixes probe-time feature negotiation, receive and transmit virtqueue management, NAPI poll loops, XDP and XSK fast paths, page-pool and DMA handling, control-virtqueue commands, RSS and multiqueue configuration, ethtool hooks, and full `net_device` lifecycle work.

The highest-value honest step in this lane is therefore a very small probe snapshot helper plus matching queue-recovery, queue-resume, `hdr_len`, and receive-path branch summaries with bounded build wiring and risk notes, not a premature runtime data-path or net-device scaffold.

## Survey findings

- `drivers/net/virtio_net.c` is present on `master` and is much larger than the earlier Phase 10 and Phase 11 starter anchors, which makes a direct first-pass Zig port a poor fit for the roadmap's bounded-delivery rule.
- the live repo already ships the Phase 10 virtio groundwork in `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, and the matching `zigux/tests/phase10_build.zig` path.
- that Phase 10 footing now reaches core-side status sequencing, feature negotiation, queue callback bookkeeping, descriptor-shape metadata, notification accounting, ring-local queue-shape and notification bookkeeping, and input-side queue planning. It still does not cover the DMA-safe abstractions, queueing correctness, recovery behavior, or segmented rollout controls that the roadmap requires before real virtio_net data-path work can land honestly.
- this checkpoint has now been re-verified against surveyed `master` snapshot `5535f26fc9b9b92751c509c5d591101994943cc3`, with the same probe snapshot, queue-recovery, queue-resume, `hdr_len`, and receive-path helpers still defining the live bounded footing.
- the Phase 12 lane now consists of a dedicated build file, `make -C zigux phase12`, the survey gate, this note, `drivers/net/virtio_net.zig`, and a focused direct test for the new starter. The shared Phase 12 build should run both the survey gate and the direct probe-starter gate so stale build wiring cannot quietly park the driver slice.
- the landed starter records one bounded queueing and recovery-facing step from `virtnet_probe()`: negotiated feature counts, queue-pair fallback, control-virtqueue presence, mergeable-buffer mode, an explicit RSS outcome summary that distinguishes active, downgraded, hash-report-only, and unavailable states, and whether probe should treat the device as stable, renegotiate features, or reset-required.
- the lane now also lands one small queue-recovery follow-up: the probe snapshot records an explicit queue recovery action that distinguishes bounded queue-pair clamping from true single-queue fallback, plus renegotiating features and requiring reset when the control-virtqueue path or negotiated feature set cannot support the requested topology.
- the lane now also lands one bounded queue-resume summary follow-up: after that freeze, the lab can report whether the remembered queue plan is ready to resume immediately, needs feature renegotiation, or still requires reset, while keeping the data-queue, control-queue, and RSS rebuild requirements explicit before any live queue activation.
- the lane now also lands one tiny header-shape follow-up: the probe snapshot mirrors the `hdr_len` branch in `virtnet_probe()` so reviewability now distinguishes legacy headers, mergeable-or-version1 headers, hash-report headers, and UDP-tunnel headers without claiming any live queue activation or packet-path behavior.
- the lane now also lands one bounded queue-recovery summary follow-up: the lab can freeze the last in-memory queue topology and recovery posture, refuse fresh probe snapshots while recovery is in flight, and clear stale planning state after restore while preserving the remembered queue-pair count, total queue count, control-queue placement, RSS summary, and reset or renegotiation intent.
- the lane now also lands one bounded receive-path follow-up: the probe snapshot records whether probe should expect small buffers, mergeable receive buffers, or big-packet refill pressure, whether `any_header_sg` keeps header and data combined or forces a separate header scatterlist entry, how much headroom must be preserved for that path, and whether an XDP request stays ready or blocked by split-header or big-packet constraints.

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
- the landed `phase12-virtio-net-queue-resume-summary`
- the landed `phase12-virtio-net-receive-path-summary`
- the still-blocked `phase12-virtio-net-runtime-data-path`

This keeps the lane explicit without overstating progress: Zigux now has a reviewable Phase 12 probe snapshot starter plus the bounded queue-recovery summary follow-up, the queue-resume summary follow-up, the newer header-shape follow-up, and the receive-path follow-up, but it still does not claim DMA-backed queue setup, NAPI, control-virtqueue commands, or a usable net-driver lifecycle.

## Rollback And Reversible Delivery

- owner: `Network Driver Lane`
- rollback owner: `Network Driver Lane`
- fallback path: keep `drivers/net/virtio_net.c` as the source of truth, keep the already-landed `drivers/net/virtio_net.zig` probe snapshot and bounded follow-up helpers additive-only, and drop the `phase12-virtio-net-tests` plus `phase12-virtio-net-survey-tests` entries from `zigux/tests/phase12_build.zig` if the shared Phase 12 packet needs to retreat.
- reversible delivery evidence: this Phase 12 packet is bounded to one additive starter, one manifest-backed survey gate, and shared build wiring around preexisting Phase 10 virtio foundations, so the review surface can be removed without inventing a second network-driver runtime path or mutating the Linux anchor.
- rollback drill: run `make -C zigux phase12-validate`; if the virtio-net packet is the only failing slice, repair `Documentation/zigux/phase12-virtio-net-survey.md`, `zigux/tests/phase12_virtio_net_manifest.json`, or the bounded `zigux/tests/phase12_virtio_net{,_survey}.zig` packet first, otherwise remove the `phase12-virtio-net-tests` and `phase12-virtio-net-survey-tests` entries from `zigux/tests/phase12_build.zig`, keep `drivers/net/virtio_net.c` and the already-landed bounded Zig helpers unchanged, then rerun `make -C zigux phase12-validate` followed by `zig build test --build-file zigux/tests/phase12_build.zig --summary all`.

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

Keep this lane on another probe-only capability handoff, most likely a tiny mergeable-refill or minimum-buffer summary, until the roadmap-approved DMA and queueing substrate exists for a truthful follow-up beyond the current probe snapshot, queue-recovery summary, queue-resume summary, `hdr_len`, and receive-path helpers.
