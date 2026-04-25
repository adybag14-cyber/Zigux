# Phase 12 Virtio SCSI Survey

This document records the bounded Phase 12 survey lane around `drivers/scsi/virtio_scsi.c`.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_SLICE=virtio-scsi-survey`
- scope: survey manifest, dedicated survey gate, shared Phase 12 build wiring, a lane note that compares the live repo state against the roadmap, and the first queue-layout starter for `drivers/scsi/virtio_scsi.zig`
- product boundary:
  - `zigux/tests/phase12_virtio_scsi_manifest.json`
  - `zigux/tests/phase12_virtio_scsi_survey.zig`
  - `zigux/tests/phase12_virtio_scsi.zig`
  - `zigux/tests/phase12_build.zig`
  - `Documentation/zigux/phase12-virtio-scsi-survey.md`
  - `Documentation/zigux/phase12-virtio-scsi-slice.md`
  - `drivers/scsi/virtio_scsi.zig`

## Why this slice exists

The Phase 12 roadmap explicitly names `drivers/scsi/virtio_scsi.c` as a complex production-driver target, and the live repo now has the first bounded `drivers/scsi/virtio_scsi.zig` starter.

That matters because `virtio_scsi.c` is not a small helper. The live file is 1,106 lines and mixes probe-time config reads, control and event virtqueue wiring, blk-mq request-queue fanout, command submission and completion, TMF and async notification handling, host scanning, and PM freeze or restore behavior.

The highest-value honest move in this lane is therefore still a narrow checkpoint: keep the survey artifacts, but pair them with a tiny in-memory queue-layout starter instead of pretending the rest of the driver is ready.

## Survey findings

- `drivers/scsi/virtio_scsi.c` is present on `master` and is large enough to cross multiple subsystem boundaries at once: virtio config, virtqueue topology, SCSI host setup, blk-mq queue planning, event handling, TMF, and recovery.
- the live repo already ships the Phase 10 virtio groundwork in `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, and the matching `zigux/tests/phase10_build.zig` path.
- that footing now reaches core-side status sequencing, feature negotiation, queue callback bookkeeping, descriptor-shape metadata, notification accounting, and ring-local queue-shape bookkeeping. It still does not cover the queue ownership, DMA-safe request buffers, SCSI-host lifecycle, or recovery behavior that the roadmap requires before real virtio_scsi work can land honestly.
- the live repo also now ships a small `drivers/scsi/virtio_scsi.zig` queue-family planner that models the control, event, request, and `request_poll` queue split derived from the Linux driver's request-queue count and poll-queue hint, while preserving the rule that one default request queue must remain.
- the next honest driver-facing step is one tiny recovery helper that freezes request planning and event recycling intent across transport freeze and restore before any blk-mq request flow, TMF handling, SCSI host registration, or DMA-backed queue work.

## Recorded gaps

The survey manifest now records:

- the landed `phase12-build-gate`
- the landed `phase12-make-target`
- the landed `phase12-virtio-core-foundation`
- the landed `phase12-virtio-ring-foundation`
- the landed `phase12-virtio-scsi-survey-gate`
- the landed `phase12-virtio-scsi-survey-note`
- the landed `phase12-virtio-scsi-driver-starter`
- the landed `phase12-virtio-scsi-driver-tests`
- the landed `phase12-virtio-scsi-slice-note`
- the ready-next `phase12-virtio-scsi-queue-freeze-recovery-helper`
- the still-blocked `phase12-virtio-scsi-runtime-queues-and-scan`

This keeps the lane explicit without overstating progress: Zigux now has a reviewable Phase 12 checkpoint plus a first queue-topology foothold for the SCSI anchor, but it does not yet claim command submission, host lifecycle parity, or recovery plumbing.

## Non-goals

This survey slice does not claim:

- command submission or completion helpers
- TMF or async notification helpers
- virtqueue buffer ownership or kick behavior
- `scsi_add_host()` or `scsi_scan_host()` lifecycle parity
- blk-mq queue mapping or polling support beyond the in-memory queue split
- PM freeze or restore behavior
- DMA-backed request or response buffer handling

## Gates

1. run the dedicated Phase 12 build
- `zig build test --build-file zigux/tests/phase12_build.zig`

2. run the convenience target
- `make -C zigux phase12`

## Next bounded step

Stay in the Phase 12 virtio_scsi lane and add one tiny recovery helper inside `drivers/scsi/virtio_scsi.zig` next so the lane can describe transport freeze and restore intent before any blk-mq request flow, event handling, SCSI host registration, or DMA-backed queue work.
