# Phase 12 Virtio SCSI Survey

This document records the bounded Phase 12 survey lane around `drivers/scsi/virtio_scsi.c`.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_SLICE=virtio-scsi-survey`
- scope: survey manifest, dedicated survey gate, shared Phase 12 build wiring, and a lane note that compares the live repo state against the roadmap for `drivers/scsi/virtio_scsi.zig`
- product boundary:
  - `zigux/tests/phase12_virtio_scsi_manifest.json`
  - `zigux/tests/phase12_virtio_scsi_survey.zig`
  - `zigux/tests/phase12_build.zig`
  - `Documentation/zigux/phase12-virtio-scsi-survey.md`

## Why this slice exists

The Phase 12 roadmap explicitly names `drivers/scsi/virtio_scsi.c` as a complex production-driver target, but the live repo still has no `drivers/scsi/virtio_scsi.zig` starter.

That matters because `virtio_scsi.c` is not a small helper. The live file is 1,106 lines and mixes probe-time config reads, control and event virtqueue wiring, blk-mq request-queue fanout, command submission and completion, TMF and async notification handling, host scanning, and PM freeze or restore behavior.

The highest-value honest step in this lane is therefore a survey checkpoint with bounded build wiring and risk notes, not a premature driver scaffold.

## Survey findings

- `drivers/scsi/virtio_scsi.c` is present on `master` and is large enough to cross multiple subsystem boundaries at once: virtio config, virtqueue topology, SCSI host setup, blk-mq queue planning, and event or TMF handling.
- the live repo already ships the Phase 10 virtio groundwork in `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, and the matching `zigux/tests/phase10_build.zig` path.
- that footing now reaches core-side status sequencing, feature negotiation, queue callback bookkeeping, descriptor-shape metadata, notification accounting, and ring-local queue-shape bookkeeping. It still does not cover the queue ownership, DMA-safe request buffers, SCSI-host lifecycle, or recovery behavior that the roadmap requires before real virtio_scsi work can land honestly.
- the live repo also now ships the first Phase 12 NVMe PCI starter, which confirms that the tranche can hold a bounded complex-driver foothold when the slice is narrow enough. The virtio_scsi lane does not yet have even its first survey artifacts or a starter file.
- the next honest driver-facing step is one tiny probe snapshot helper around `num_queues`, `seg_max`, `cmd_per_lun`, `max_target`, `max_lun`, `max_sectors`, and the control or event versus request virtqueue layout derived in `virtscsi_probe()`.

## Recorded gaps

The survey manifest now records:

- the landed `phase12-build-gate`
- the landed `phase12-make-target`
- the landed `phase12-virtio-core-foundation`
- the landed `phase12-virtio-ring-foundation`
- the landed `phase12-virtio-scsi-survey-gate`
- the landed `phase12-virtio-scsi-survey-note`
- the ready-next `phase12-virtio-scsi-probe-config-snapshot-starter`
- the still-blocked `phase12-virtio-scsi-runtime-queues-and-scan`

This keeps the lane explicit without overstating progress: Zigux now has a reviewable Phase 12 checkpoint for the SCSI anchor, but it does not yet claim any driver implementation.

## Non-goals

This survey slice does not claim:

- a `drivers/scsi/virtio_scsi.zig` starter
- command submission or completion helpers
- TMF or async notification helpers
- virtqueue buffer ownership or kick behavior
- `scsi_add_host()` or `scsi_scan_host()` lifecycle parity
- blk-mq queue mapping or polling support
- PM freeze or restore behavior
- DMA-backed request or response buffer handling

## Gates

1. run the dedicated Phase 12 build
- `zig build test --build-file zigux/tests/phase12_build.zig`

2. run the convenience target
- `make -C zigux phase12`

## Next bounded step

Stay in the Phase 12 virtio_scsi lane and add one tiny `drivers/scsi/virtio_scsi.zig` probe snapshot helper next so the lane can describe the `virtscsi_probe()` config-and-topology branch before any blk-mq request flow, event handling, SCSI host registration, or DMA-backed queue work.
