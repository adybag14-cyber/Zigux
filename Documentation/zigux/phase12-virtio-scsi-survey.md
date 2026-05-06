# Phase 12 Virtio SCSI Survey

This document records the bounded Phase 12 survey lane around `drivers/scsi/virtio_scsi.c`.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_SLICE=virtio-scsi-survey`
- `PHASE12_LANE=P12-L13`
- scope: survey manifest, dedicated survey gate, shared Phase 12 build wiring, and a lane note that compares the live repo state against the roadmap for `drivers/scsi/virtio_scsi.zig`
- fallback note role: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` is read-only replay evidence for degraded reads and does not own the active survey packet
- product boundary:
  - `zigux/tests/phase12_virtio_scsi_manifest.json`
  - `zigux/tests/phase12_virtio_scsi_survey.zig`
  - `zigux/tests/phase12_build.zig`
  - `Documentation/zigux/phase12-virtio-scsi-survey.md`

## Why this slice exists

The Phase 12 roadmap explicitly names `drivers/scsi/virtio_scsi.c` as a complex production-driver target.

That still matters even after the first Zigux starter landed because `virtio_scsi.c` is not a small helper. The live Linux anchor is 1,106 lines and mixes probe-time config reads, control and event virtqueue wiring, blk-mq request-queue fanout, command submission and completion, TMF and async notification handling, host scanning, and PM freeze or restore behavior.

The highest-value honest step in this lane is therefore to keep the survey, validation, and risk notes aligned with the bounded starter that now exists, rather than pretending the lane is still pre-driver or widening into premature runtime scaffolding.

## Survey findings

- `drivers/scsi/virtio_scsi.c` is present on `master` and is large enough to cross multiple subsystem boundaries at once: virtio config, virtqueue topology, SCSI host setup, blk-mq queue planning, and event or TMF handling.
- the live repo already ships the Phase 10 virtio groundwork in `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, and the matching `zigux/tests/phase10_build.zig` path.
- that footing now reaches core-side status sequencing, feature negotiation, queue callback bookkeeping, descriptor-shape metadata, notification accounting, and ring-local queue-shape bookkeeping. It still does not cover queue ownership, DMA-safe request buffers, SCSI-host lifecycle, or recovery behavior at the depth that the roadmap requires before real virtio_scsi runtime work can land honestly.
- the live repo also now ships a bounded `drivers/scsi/virtio_scsi.zig` starter, dedicated `zigux/tests/phase12_virtio_scsi.zig` coverage, and `Documentation/zigux/phase12-virtio-scsi-slice.md`. That starter is intentionally narrow: it models control, event, request, and request_poll queue-family planning in memory, preserves poll-queue clamping, keeps stable global virtqueue indexes, and records a lab-only freeze or restore summary that blocks planning while transport is frozen and clears the old queue snapshot after restore.
- the shared Phase 12 packet now also keeps the focused smoke preflight explicit: `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all` and `make -C zigux phase12-smoke` rerun the direct `virtio_scsi` starter ahead of the broader survey-backed replay, so this survey note should not leave that narrower driver-facing shard implied only by `zigux/tests/phase12_build.zig`, the Makefile, or the fallback catalog.
- the next honest driver-facing step is still one tiny probe snapshot helper around `virtscsi_probe()` config fields such as `num_queues`, `seg_max`, `cmd_per_lun`, `max_target`, `max_lun`, `max_sectors`, and the derived control or event versus request virtqueue layout.

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
- the ready-next `phase12-virtio-scsi-probe-config-snapshot-starter`
- the still-blocked `phase12-virtio-scsi-runtime-queues-and-scan`

This keeps the lane explicit without overstating progress: Zigux now has a bounded virtio_scsi queue-layout and recovery starter, but it still does not claim command submission, event completion, TMF flow, SCSI-host registration, PM callback wiring, or DMA-backed virtqueue ownership.

## Non-goals

This survey slice does not claim:

- command submission or completion helpers
- TMF or async notification helpers
- virtqueue buffer ownership or kick behavior
- `scsi_add_host()` or `scsi_scan_host()` lifecycle parity
- blk-mq queue mapping or polling support
- PM freeze or restore callback wiring
- DMA-backed request or response buffer handling

## Gates

1. run the focused smoke preflight
- `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
- `make -C zigux phase12-smoke`
- these rerun the direct `virtio_scsi` starter ahead of the broader survey-backed replay route.

2. run the dedicated Phase 12 build
- `zig build test --build-file zigux/tests/phase12_build.zig --summary all`

3. run the convenience target
- `make -C zigux phase12`

## Next bounded step

Stay in the Phase 12 virtio_scsi lane and add one tiny `drivers/scsi/virtio_scsi.zig` probe snapshot helper next so the lane can describe the `virtscsi_probe()` config-and-topology branch before any blk-mq request flow, event handling, SCSI host registration, or DMA-backed queue work.

Until that driver-local follow-up is approved, keep this survey aligned with the shared smoke-plus-build replay packet instead of letting the focused preflight shard drift back into build-file-only, Makefile-only, or fallback-catalog-only knowledge.
