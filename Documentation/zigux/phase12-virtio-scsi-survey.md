# Phase 12 Virtio SCSI Survey

This document records the bounded Phase 12 survey lane around `drivers/scsi/virtio_scsi.c`.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_SLICE=virtio-scsi-survey`
- scope: survey manifest, dedicated survey gate, shared Phase 12 build wiring, a raw GitHub fallback catalog pinned to the current inspected head, and a lane note that compares the live repo state against the roadmap for `drivers/scsi/virtio_scsi.zig`
- product boundary:
  - `zigux/tests/phase12_virtio_scsi_manifest.json`
  - `zigux/tests/phase12_virtio_scsi_survey.zig`
  - `zigux/tests/phase12_build.zig`
  - `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`
  - `Documentation/zigux/phase12-virtio-scsi-survey.md`

## Why this slice exists

The Phase 12 roadmap explicitly names `drivers/scsi/virtio_scsi.c` as a complex production-driver target.

That still matters even after the first Zigux starter landed because `virtio_scsi.c` is not a small helper. The live Linux anchor is 1,106 lines and mixes probe-time config reads, control and event virtqueue wiring, blk-mq request-queue fanout, command submission and completion, TMF and async notification handling, host scanning, and PM freeze or restore behavior.

The highest-value honest step in this lane is therefore to keep the survey, validation, and risk notes aligned with the bounded starter that now exists, rather than pretending the lane is still pre-driver or widening into premature runtime scaffolding.

## Survey findings

- `drivers/scsi/virtio_scsi.c` is present on `master` and is large enough to cross multiple subsystem boundaries at once: virtio config, virtqueue topology, SCSI host setup, blk-mq queue planning, and event or TMF handling.
- the live repo already ships the Phase 10 virtio groundwork in `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, and the matching `zigux/tests/phase10_build.zig` path.
- that footing now reaches core-side status sequencing, feature negotiation, queue callback bookkeeping, descriptor-shape metadata, notification accounting, and ring-local queue-shape bookkeeping. It still does not cover queue ownership, DMA-safe request buffers, SCSI-host lifecycle, or recovery behavior at the depth that the roadmap requires before real virtio_scsi runtime work can land honestly.
- the shared Phase 12 tranche wiring now also includes `make -C zigux phase12`, so the survey lane and the bounded direct test lane stay runnable through the same entry point as the other complex-driver checkpoints instead of drifting into one-off commands.
- the live repo also now ships a bounded `drivers/scsi/virtio_scsi.zig` starter, dedicated `zigux/tests/phase12_virtio_scsi.zig` coverage, and `Documentation/zigux/phase12-virtio-scsi-slice.md`. That starter is intentionally narrow: it models control, event, request, and request_poll queue-family planning in memory, preserves poll-queue clamping, keeps stable global virtqueue indexes, records a lab-only freeze or restore summary that blocks planning while transport is frozen and clears the old queue snapshot after restore, captures one probe snapshot of `virtscsi_probe()` config fields such as `num_queues`, `seg_max`, `cmd_per_lun`, `max_target`, `max_lun`, and `max_sectors` alongside the derived control, event, default-request, and poll-request virtqueue layout, now also lands one tiny host-limit summary helper that clamps `cmd_per_lun` against a synthetic `can_queue` while recording `max_target`, `max_lun`, `max_sectors`, and `nr_hw_queues` before any `scsi_host_alloc()`, `scsi_add_host()`, or `scsi_scan_host()` work is attempted, and keeps one bounded io-queue-map plus recovery-restore summary in memory so default, read, and poll map counts, queue offsets, virtio-affinity intent, and poll-map restore pressure stay reviewable before any live `map_queues` callback or CPU-affinity wiring is attempted.
- the lane now also records a commit-pinned raw GitHub fallback catalog in `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, originally verified against inspected `master` head `5ecf3870d48d43e7a718b620b02ab9f60c0b969f`, so future scheduled runs can recover the exact anchor, starter, survey, build, validator, and note files even if connector-backed reads are flaky.
- that fallback packet is now historical evidence, not the current risk story: the older packet still captures one unrelated shared-validator failure on that older inspected head, but the current replay on `master` head `cf92730c0711f5d0705b5c35aa8dfbf777219bcc` now reports `PHASE12_VALIDATION=pass` while the focused `zig test zigux/tests/phase12_virtio_scsi_survey.zig` replay still passes `1/1` tests.

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
- the landed `phase12-virtio-scsi-raw-github-fallback-catalog`
- the landed `phase12-virtio-scsi-probe-config-snapshot-starter`
- the landed `phase12-virtio-scsi-host-limit-summary-starter`
- the landed `phase12-virtio-scsi-io-queue-map-summary-starter`
- the still-blocked `phase12-virtio-scsi-runtime-queues-and-scan`

This keeps the lane explicit without overstating progress: Zigux now has a bounded virtio_scsi queue-layout, recovery, probe snapshot, host-limit summary, and io-queue-map starters plus an exact raw fallback evidence packet, but it still does not claim command submission, event completion, TMF flow, SCSI-host registration, PM callback wiring, or DMA-backed virtqueue ownership.

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

1. run the dedicated Phase 12 build
- `zig build test --build-file zigux/tests/phase12_build.zig`

2. run the convenience target
- `make -C zigux phase12`

## Next bounded step

Keep this lane on survey or validation work until the roadmap-approved queue ownership, SCSI-host lifecycle, and DMA-backed transport substrate exists for a truthful follow-up beyond the current queue-layout, recovery, probe snapshot, host-limit summary, and io-queue-map starters.
