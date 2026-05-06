# Phase 12 Virtio Net Survey

This document records the bounded Phase 12 survey lane around `drivers/net/virtio_net.c`, the first landed Zigux starter tied to it, and the directly coupled syntax-lab, queue-recovery, receive-refill, transmit-recycle, and mergeable-buffer-length follow-ups that keep the lane reviewable without widening into runtime data-path work.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_SLICE=virtio-net-survey`
- scope: survey manifest, dedicated survey gate, shared Phase 12 build wiring, the `drivers/net/virtio_net.zig` probe snapshot starter plus the direct `phase12_virtio_net_syntax_lab.zig` smoke shard, its queue-recovery, receive-refill, transmit-recycle, and mergeable-buffer-length follow-ups, the segmented rollout boundary that keeps the active tranche below live DMA-backed work, and a lane note that compares the live repo state against the roadmap for the broader driver
- product boundary:
  - `zigux/tests/phase12_virtio_net_manifest.json`
  - `zigux/tests/phase12_virtio_net_survey.zig`
  - `zigux/tests/phase12_virtio_net.zig`
  - `zigux/tests/phase12_virtio_net_syntax_lab.zig`
  - `zigux/tests/phase12_build.zig`
  - `Documentation/zigux/phase12-virtio-net-survey.md`
- public fallback posture: shared-tree-only anchor; unlike `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, this `virtio_net` note is not a commit-pinned raw GitHub fallback artifact.

## Why this slice exists

The Phase 12 roadmap explicitly names `drivers/net/virtio_net.c` as a complex production-driver target, and the live repo now carries only the first tiny `drivers/net/virtio_net.zig` starter for that lane.

That still matters because `virtio_net.c` is not a small leaf helper. The live file is 7,288 lines and mixes probe-time feature negotiation, receive and transmit virtqueue management, NAPI poll loops, XDP and XSK fast paths, page-pool and DMA handling, control-virtqueue commands, RSS and multiqueue configuration, ethtool hooks, and full `net_device` lifecycle work.

The highest-value honest step in this lane is therefore a very small probe snapshot helper plus tightly bounded queue-planning follow-ups with explicit build wiring and risk notes, not a premature runtime data-path or net-device scaffold.

## Survey findings

- `drivers/net/virtio_net.c` is present on `master` and is much larger than the earlier Phase 10 and Phase 11 starter anchors, which makes a direct first-pass Zig port a poor fit for the roadmap's bounded-delivery rule.
- the live repo already ships the Phase 10 virtio groundwork in `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, and the matching `zigux/tests/phase10_build.zig` path.
- that Phase 10 footing now reaches core-side status sequencing, feature negotiation, queue callback bookkeeping, descriptor-shape metadata, notification accounting, ring-local queue-shape and notification bookkeeping, and input-side queue planning. It still does not cover the DMA-safe abstractions, queueing correctness, recovery behavior, or segmented rollout controls that the roadmap requires before real virtio_net data-path work can land honestly.
- the Phase 12 lane now consists of the focused direct `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all` preflight, the Linux-style `make -C zigux phase12-smoke` replay, the dedicated build file, `make -C zigux phase12`, the survey gate, this note, `drivers/net/virtio_net.zig`, and focused direct tests for the probe starter, the direct syntax-lab export gate, its queue-recovery, receive-refill, transmit-recycle, and mergeable-buffer-length follow-ups, and the segmented rollout boundary that keeps the active tranche below live DMA-backed work. The shared Phase 12 build should run both the survey gate and the direct probe-starter-plus-syntax-lab smoke shard so stale build wiring cannot quietly park the driver slice, while the smoke preflight keeps the direct driver packet explicit ahead of the broader survey-backed replay.
- unlike `nvme_pci` and `virtio_scsi`, the live `virtio_net` packet still does not ship a separate `Documentation/zigux/phase12-virtio-net-slice.md`, and that remains the truthful boundary on `master`: the direct probe starter, syntax-lab export gate, queue-recovery, receive-refill, transmit-recycle, mergeable-buffer-length, and segmented-rollout cues are still one survey-backed review packet rather than a split starter-plus-slice doc surface.
- the landed starter records one bounded queueing and recovery-facing step from `virtnet_probe()`: negotiated feature counts, queue-pair fallback, control-virtqueue presence, mergeable-buffer mode, RSS or hash-report capability, whether probe should treat the device as stable, renegotiate features, or reset-required, and a narrow freeze or resume summary that keeps queue rebuild scope explicit for data queues, control-vq restore, RSS reapply, and fresh probe replay after recovery.
- the direct syntax-lab shard keeps one more reviewability step explicit without widening the runtime boundary: it proves the bounded probe descriptor, recovery enums, queue-resume enums, receive-refill enums, and mergeable-buffer planning enums remain reachable from the shipped direct smoke packet even when the survey gate itself stays focused on tranche-level truthfulness.
- the newly landed receive-refill follow-up keeps one more packet-path step explicit without widening into live DMA or NAPI work: buffer mode stays visible as single-buffer versus mergeable-buffer refill, receive queue counts survive the frozen recovery snapshot, clamp-versus-single-queue recovery intent survives into the refill plan, control-vq restore and RSS reapply needs remain attached to that plan, and post-restore probe replay is still required before the lane can pretend a live refill path exists.
- the newly landed transmit-recycle follow-up keeps one more completion-side step explicit without widening into live DMA or NAPI work: packet return ordering stays visible as data-only reuse versus control-queue restore or RSS-reapply ordering, transmit queue counts survive the frozen recovery snapshot, and receive-refill coordination remains explicit before the lane can pretend a live completion path exists.
- the newly landed mergeable-buffer-length follow-up keeps one more throughput-facing handoff explicit without widening into live DMA or NAPI work: once a frozen mergeable snapshot exists, the lab can mirror `get_mergeable_buf_len()` by recording whether the selected buffer length stays at the observed average packet size, clamps to the minimum floor, caps at page payload, or falls back to page-minus-room sizing when XDP headroom reserves aligned room for `skb_shared_info`.
- the active packet now treats those landed probe, syntax-lab, queue-recovery, receive-refill, transmit-recycle, and mergeable-buffer-length steps as a segmented rollout boundary: the runtime-data-path boundary remains blocked until roadmap-approved DMA-safe abstractions and queueing substrate work exist, so the current tranche still stops short of live page-pool DMA, refill loops, XDP execution, NAPI, control-virtqueue commands, or net-device lifecycle work.

## Recorded gaps

The survey manifest now records:

- the landed `phase12-build-gate`
- the landed `phase12-make-target`
- the landed `phase12-virtio-core-foundation`
- the landed `phase12-virtio-ring-foundation`
- the landed `phase12-virtio-net-survey-gate`
- the landed `phase12-virtio-net-survey-note`
- the landed `phase12-virtio-net-syntax-lab-gate`
- the landed `phase12-virtio-net-probe-snapshot-starter`
- the landed `phase12-virtio-net-queue-recovery-followup`
- the landed `phase12-virtio-net-receive-refill-followup`
- the landed `phase12-virtio-net-transmit-recycle-followup`
- the landed `phase12-virtio-net-mergeable-buffer-length-summary`
- the landed `phase12-virtio-net-segmented-rollout-boundary`
- the still-blocked `phase12-virtio-net-runtime-data-path`

This keeps the lane explicit without overstating progress: Zigux now has a reviewable Phase 12 probe snapshot starter, a direct syntax-lab export gate, a bounded queue-recovery follow-up, a bounded receive-refill planning follow-up, a bounded transmit-recycle follow-up, a bounded mergeable-buffer-length follow-up, and an explicit segmented rollout boundary, while the broader runtime-data-path boundary still stays below live DMA-backed queue setup, NAPI, control-virtqueue commands, or a usable net-driver lifecycle.

## Non-goals

This survey slice does not claim:

- NAPI poll behavior
- page-pool or DMA-backed buffer management
- XDP or XSK fast paths
- control-virtqueue command helpers beyond presence or fallback reporting
- RSS table programming, ethtool hooks, or channel reconfiguration
- `net_device` registration, open or close flows, suspend or resume, or teardown parity

## Gates

1. run the focused smoke preflight
- `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
- `make -C zigux phase12-smoke`
- these rerun the direct `virtio_net` probe-and-follow-up packet plus the bounded syntax-lab gate ahead of the broader survey-backed replay route.

2. run the dedicated Phase 12 build
- `zig build test --build-file zigux/tests/phase12_build.zig --summary all`

3. run the convenience target
- `make -C zigux phase12`

## Next bounded step

Keep this lane parked unless fresh repo inspection finds directly coupled drift in the landed probe snapshot, syntax-lab, queue-recovery, receive-refill, transmit-recycle, mergeable-buffer-length, or segmented-rollout-boundary packet.

Keep this survey note as the truthful driver-local source of truth for the current `virtio_net` packet until live master actually lands a separate starter-plus-slice surface; until then, avoid inventing a `phase12-virtio-net-slice.md` file that would only restate the already-shipped survey-backed boundary.

If live master still matches this note on the next same-lane pass, the next honest review-surface follow-through is not another docs-root syntax-lab sync because `Documentation/zigux/README.md` already names `zigux/tests/phase12_virtio_net_syntax_lab.zig` beside `zigux/tests/phase12_virtio_net.zig` and `zigux/tests/phase12_virtio_net_survey.zig`. Keep the packet parked unless a fresh same-family survey, manifest, or build-surface drift appears before anyone reopens the false slice-note path.

The next honest same-family move after that reviewability repair stays on the blocked runtime-data-path boundary: any future follow-up still needs roadmap-approved DMA-safe abstractions and queueing substrate work before Zigux can claim live page-pool DMA, refill loops, XDP execution, NAPI, control-virtqueue commands, or net-device lifecycle behavior.
