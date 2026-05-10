# Phase 12 Virtio Net Survey

This document records the bounded Phase 12 survey lane around `drivers/net/virtio_net.c`, the first landed Zigux starter tied to it, and the directly coupled syntax-lab, queue-recovery, receive-refill, control-queue-restore, mergeable-buffer-length, and repeated-recovery-cycle follow-ups plus the still-ready-next transmit-recycle review surface that keep the lane reviewable without widening into runtime data-path work.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_SLICE=virtio-net-survey`
- scope: survey manifest, dedicated survey gate, shared Phase 12 build wiring, the `drivers/net/virtio_net.zig` probe snapshot starter plus the direct `phase12_virtio_net_syntax_lab.zig` smoke shard, its queue-recovery, receive-refill, control-queue-restore, mergeable-buffer-length, and repeated-recovery-cycle follow-ups, the still-ready-next transmit-recycle review surface, the segmented rollout boundary that keeps the active tranche below live DMA-backed work, and `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, the anti-overlap lane note that compares the live repo state against the roadmap for the broader driver
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
- that Phase 10 footing now reaches core-side status sequencing, feature negotiation, queue callback bookkeeping, descriptor-shape metadata, notification accounting, ring-local queue-shape and notification bookkeeping, and input-side queue planning. It still does not cover the DMA-safe abstractions, queueing correctness, or throughput and recovery parity that the roadmap requires before real virtio_net data-path work can land honestly, and the current packet only addresses the segmented rollout requirement as a review boundary rather than a live transport or DMA substrate.
- the Phase 12 lane now consists of the focused direct `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all` preflight, the Linux-style `make -C zigux phase12-smoke` replay, the dedicated build file, `make -C zigux phase12`, the survey gate, this note, `drivers/net/virtio_net.zig`, and focused direct tests for the probe starter, the direct syntax-lab export gate, its queue-recovery, receive-refill, control-queue-restore, mergeable-buffer-length, and repeated-recovery-cycle follow-ups, plus the still-ready-next transmit-recycle review surface, and the segmented rollout boundary that keeps the active tranche below live DMA-backed work. The shared Phase 12 build should run both the survey gate and the direct probe-starter-plus-syntax-lab smoke shard so stale build wiring cannot quietly park the driver slice, while the smoke preflight keeps the direct driver packet explicit ahead of the broader survey-backed replay.
- unlike `nvme_pci` and `virtio_scsi`, the live `virtio_net` packet still does not ship a separate `Documentation/zigux/phase12-virtio-net-slice.md`, and that remains the truthful boundary on `master`: the direct probe starter, syntax-lab export gate, queue-recovery, receive-refill, control-queue-restore, mergeable-buffer-length, repeated-recovery-cycle, the still-ready-next transmit-recycle cue, and segmented-rollout cues are still one survey-backed review packet rather than a split starter-plus-slice doc surface.
- the landed starter records one bounded queueing and recovery-facing step from `virtnet_probe()`: negotiated feature counts, queue-pair fallback, control-virtqueue presence, mergeable-buffer mode, RSS or hash-report capability, whether probe should treat the device as stable, renegotiate features, or reset-required, and a narrow freeze or resume summary that keeps queue rebuild scope explicit for data queues, control-vq restore, RSS reapply, and fresh probe replay after recovery.
- the direct syntax-lab shard keeps one more reviewability step explicit without widening the runtime boundary: it proves the bounded probe descriptor, recovery enums, queue-resume enums, receive-refill enums, control-queue-restore enums, and mergeable-buffer planning enums remain reachable from the shipped direct smoke packet even when the survey gate itself stays focused on tranche-level truthfulness, and it now also replays repeated recovery cycles so `recovery_generation` stays explicit across freeze, restore, control-queue-restore, and recovery-ownership handoffs.
- the newly landed receive-refill follow-up keeps one more packet-path step explicit without widening into live DMA or NAPI work: buffer mode stays visible as single-buffer versus mergeable-buffer refill, receive queue counts survive the frozen recovery snapshot, clamp-versus-single-queue recovery intent survives into the refill plan, control-vq restore and RSS reapply needs remain attached to that plan, and post-restore probe replay is still required before the lane can pretend a live refill path exists.
- the newly landed control-queue-restore follow-up keeps one more recovery-governance step explicit without widening into live control traffic, DMA, or NAPI work: restore disposition stays visible as not-required versus restore-after-data-queue-rebuild or restore-before-RSS-reapply, queue-pair counts survive the frozen recovery snapshot, and post-restore probe replay remains explicit before the lane can pretend live control-virtqueue commands exist.
- the still-ready-next transmit-recycle follow-up remains the next bounded completion-side step before this review packet can call it landed: packet return ordering is already modeled in `drivers/net/virtio_net.zig`, but the current manifest and survey gate still keep transmit-recycle as `ready_next` until the lane records that completion-side surface with the same direct test and review-note evidence used by the landed follow-ups.
- the queueing packet now also carries one driver-local recovery ownership order note: the frozen snapshot owns remembered queue shape and recovery intent until data queues are rebuilt, control-virtqueue restore owns queue-pair governance after that data-queue rebuild when a control queue exists, RSS reapply owns steering-state handoff only after the control queue is back, receive refill stays subordinate to the resumed data queues, transmit recycle remains last because completion-side queue reuse still depends on receive-refill coordination, and `post_restore_probe_replay` is the steady-state owner that revalidates the restored queue counts, fallback reason, and remembered recovery action before the lane can treat control-queue or RSS state as settled again.
- the newly landed mergeable-buffer-length follow-up keeps one more throughput-facing handoff explicit without widening into live DMA or NAPI work: once a frozen mergeable snapshot exists, the lab can mirror `get_mergeable_buf_len()` by recording whether the selected buffer length stays at the observed average packet size, clamps to the minimum floor, caps at page payload, or falls back to page-minus-room sizing when XDP headroom reserves aligned room for `skb_shared_info`.
- the active packet now treats those landed probe, syntax-lab, queue-recovery, receive-refill, control-queue-restore, mergeable-buffer-length, and repeated-recovery-cycle steps plus the still-ready-next transmit-recycle cue as a segmented rollout boundary: the runtime-data-path boundary remains blocked until roadmap-approved DMA-safe abstractions, queueing correctness substrate work, and throughput plus recovery parity evidence exist, so the current tranche still stops short of live page-pool DMA, refill loops, XDP execution, NAPI, control-virtqueue commands, or net-device lifecycle work.
- use `Documentation/zigux/phase12-release-closure-checklist.md` as the PMO companion when judging whether this survey-backed packet is close enough to describe the active Phase 12 tranche as release-closed.
- keep `Documentation/zigux/phase12-release-coordination-matrix.md` visible beside that same PMO closure companion so the compact lane-owner split, fallback split, and smoke-set summary stay reviewable without flattening the `virtio_net` lane into broader PMO prose.
- when the local runtime does not provide `zig` on `PATH`, keep the same smoke-first replay order and rerun only the shipped Make routes with `ZIG=<attached-zig-path>` instead of inventing a driver-local or `virtio_net`-specific fallback entrypoint.

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
- the landed `phase12-virtio-net-control-queue-restore-followup`
- the ready-next `phase12-virtio-net-transmit-recycle-followup`
- the landed `phase12-virtio-net-recovery-ownership-note`
- the landed `phase12-virtio-net-mergeable-buffer-length-summary`
- the landed `phase12-virtio-net-segmented-rollout-boundary`
- the still-blocked `phase12-virtio-net-runtime-data-path`

This keeps the lane explicit without overstating progress: Zigux now has a reviewable Phase 12 probe snapshot starter, a direct syntax-lab export gate, a bounded queue-recovery follow-up, a bounded receive-refill planning follow-up, a bounded control-queue-restore planning follow-up, a bounded recovery-ownership note, a bounded mergeable-buffer-length follow-up, a repeated-recovery-cycle syntax-lab replay, and an explicit segmented rollout boundary, while the transmit-recycle follow-up remains the next bounded completion-side step and the broader runtime-data-path boundary still stays below live DMA-backed queue setup, NAPI, control-virtqueue commands, or a usable net-driver lifecycle.

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

4. If the local runtime does not provide `zig` on `PATH`, keep the same smoke-first order and rerun the shipped Make routes with an attached toolchain override instead of inventing a new `virtio_net`-specific or Phase 12 entrypoint.
- `make -C zigux phase12-smoke ZIG=<attached-zig-path>`
- `make -C zigux phase12 ZIG=<attached-zig-path>`
- This is an environment override for the existing replay packet, not a validator-first, driver-local, or `phase12-validate` route.

Use `Documentation/zigux/phase12-release-closure-checklist.md` as the PMO companion when judging whether this survey-backed packet is close enough to describe the active Phase 12 tranche as release-closed.

Keep `Documentation/zigux/phase12-release-coordination-matrix.md` visible beside that same PMO closure companion when judging whether the compact lane-owner split, fallback split, and smoke-set summary still match this survey-backed packet.

## Next bounded step

Keep this lane parked unless fresh repo inspection finds directly coupled drift in the landed probe snapshot, syntax-lab, queue-recovery, receive-refill, control-queue-restore, mergeable-buffer-length, repeated-recovery-cycle, or segmented-rollout-boundary packet, or unless the next same-family run is explicitly taking up the still-ready-next transmit-recycle follow-up.

Keep this survey note as the truthful driver-local source of truth for the current `virtio_net` packet until live master actually lands a separate starter-plus-slice surface; until then, avoid inventing a `phase12-virtio-net-slice.md` file that would only restate the already-shipped survey-backed boundary.

The older shared tests-root release-readiness reminder is already closed on `master`: `zigux/tests/README.md` already keeps `Documentation/zigux/phase12-release-readiness-survey.md` explicit beside the shared smoke-first packet, the PMO closure companion, the compact release-coordination matrix, the two anti-overlap companions, the shared fallback-overview note, the freeze-boundary reminder, and the shipped smoke-first plus shared-build replay order.

With that shared reminder already settled, the next honest same-family move stays on the blocked runtime-data-path boundary after the ready-next transmit-recycle follow-up: any future follow-up still needs roadmap-approved DMA-safe abstractions, queueing correctness substrate work, and throughput plus recovery parity evidence before Zigux can claim live page-pool DMA, refill loops, XDP execution, NAPI, control-virtqueue commands, or net-device lifecycle behavior.
