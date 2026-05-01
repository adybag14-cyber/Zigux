# Phase 12 Virtio SCSI Survey

This document records the bounded Phase 12 survey lane around `drivers/scsi/virtio_scsi.c`.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_SLICE=virtio-scsi-survey`
- scope: survey manifest, dedicated survey gate, shared Phase 12 build wiring, a raw GitHub fallback catalog pinned to one inspected head, and a lane note that compares the live repo state against the roadmap for `drivers/scsi/virtio_scsi.zig`
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
- the live repo also now ships a bounded `drivers/scsi/virtio_scsi.zig` starter, dedicated `zigux/tests/phase12_virtio_scsi.zig` coverage, and `Documentation/zigux/phase12-virtio-scsi-slice.md`. That starter is intentionally narrow: it models control, event, request, and request_poll queue-family planning in memory, preserves poll-queue clamping, keeps stable global virtqueue indexes, records a lab-only freeze or restore summary that blocks planning while transport is frozen, now also blocks queue-depth capture until restore, and clears the old queue snapshot after restore, captures one probe snapshot of `virtscsi_probe()` config fields such as `num_queues`, `seg_max`, `cmd_per_lun`, `max_target`, `max_lun`, and `max_sectors` alongside the derived control, event, default-request, and poll-request virtqueue layout, now also lands one tiny host-limit summary helper that clamps `cmd_per_lun` against a synthetic `can_queue` while recording `max_target`, `max_lun`, `max_sectors`, and `nr_hw_queues` before any `scsi_host_alloc()`, `scsi_add_host()`, or `scsi_scan_host()` work is attempted, adds one tiny queue-depth summary helper that mirrors `virtscsi_change_queue_depth()` by clamping a requested depth against effective `cmd_per_lun` while keeping `track_queue_depth` reviewable before any live host registration or blk-mq request flow, and keeps one bounded io-queue-map plus recovery-restore summary in memory so default, read, and poll map counts, queue offsets, virtio-affinity intent, and poll-map restore pressure stay reviewable before any live `map_queues` callback or CPU-affinity wiring is attempted.
- the lane now also records a commit-pinned raw GitHub fallback catalog in `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, currently pinned to historical inspected `master` head `7d653d8c5e57207763c07c1b1d020b514738c7f3`. That archival packet still lets future scheduled runs recover the exact anchor, starter, survey, build, validator, and note files when connector-backed reads are flaky, while the separate fallback-evidence lanes own any exact live-head or hash refresh. The catalog's `Latest repo-head recheck` section is retained as the last recorded comparison that landed with this archival packet; it is historical maintenance evidence rather than a promise that the cited newer `master` head is still the newest one today.
- the pinned fallback packet also preserves one historical degraded-workflow replay from inspected head `7d653d8c5e57207763c07c1b1d020b514738c7f3`: the archived `python3 scripts/zigux/validate-phase12.py` replay failed on four unrelated shared-packet drifts while the focused `zig test zigux/tests/phase12_virtio_scsi_survey.zig` replay still passed `1/1` tests.
- the exact archived validator miss list now stays in `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, so this survey note can point at the pinned fallback evidence without repeating cross-lane details or implying those misses are still current on newer Phase 12 heads.

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
- the landed `phase12-virtio-scsi-queue-depth-summary-starter`
- the landed `phase12-virtio-scsi-io-queue-map-summary-starter`
- the still-blocked `phase12-virtio-scsi-runtime-queues-and-scan`

This keeps the lane explicit without overstating progress: Zigux now has a bounded virtio_scsi queue-layout, recovery, probe snapshot, host-limit summary, queue-depth summary, and io-queue-map starters plus an exact raw fallback evidence packet, but it still does not claim command submission, event completion, TMF flow, SCSI-host registration, PM callback wiring, or DMA-backed virtqueue ownership.

## Rollback And Reversible Delivery

- owner: `Storage Driver Lane`
- rollback owner: `Storage Driver Lane`
- fallback path: keep `drivers/scsi/virtio_scsi.c` as the source of truth, keep the bounded `drivers/scsi/virtio_scsi.zig` queue-layout, recovery, probe snapshot, host-limit summary, queue-depth summary, and io-queue-map helpers reviewable in isolation, keep `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` pinned to its inspected commit for degraded readback, and drop the direct `phase12-virtio-scsi-tests` plus `phase12-virtio-scsi-survey-tests` entries out of `zigux/tests/phase12_build.zig` if the shared packet regresses.
- reversible delivery evidence: this Phase 12 packet only adds one bounded `drivers/scsi/virtio_scsi.zig` starter, its paired `zigux/tests/phase12_virtio_scsi.zig` and `zigux/tests/phase12_virtio_scsi_survey.zig` review gates, the raw fallback catalog, and this survey note around the existing C anchor, so the lane can be narrowed again without inventing DMA-backed request ownership, `Scsi_Host` lifecycle parity, or blk-mq runtime claims.
- rollback drill: run `make -C zigux phase12-validate`; if the virtio_scsi packet is the only failing slice, repair `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, or `zigux/tests/phase12_virtio_scsi_survey.zig` first when only the reviewability record drifted, otherwise remove the `phase12-virtio-scsi-tests` and `phase12-virtio-scsi-survey-tests` entries from `zigux/tests/phase12_build.zig`, keep `drivers/scsi/virtio_scsi.c` plus the bounded Zig starter unchanged, then rerun `make -C zigux phase12-validate` followed by `zig build test --build-file zigux/tests/phase12_build.zig --summary all` so the shared Phase 12 tranche stays truthful while the survey packet is repaired.

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

1. run the shared Phase 12 validator-first path
- `python3 scripts/zigux/validate-phase12.py`
- `make -C zigux phase12-validate`

2. run the dedicated Phase 12 build
- `zig build test --build-file zigux/tests/phase12_build.zig --summary all`

3. run the convenience target
- `make -C zigux phase12`

## Next bounded step

Keep this lane on survey or validation work until the roadmap-approved queue ownership, SCSI-host lifecycle, and DMA-backed transport substrate exists for a truthful follow-up beyond the current queue-layout, recovery, probe snapshot, host-limit summary, queue-depth summary, and io-queue-map starters.