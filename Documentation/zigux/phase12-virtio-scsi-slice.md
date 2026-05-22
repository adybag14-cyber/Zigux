# Phase 12 virtio_scsi Slice
- `PHASE12_SLICE=virtio-scsi-rollback-evidence`
- reread against live `master` and the active `P12-L13` survey packet on `2026-05-21`
- lane: `complex-drivers-infra`
- anchor: `drivers/scsi/virtio_scsi.c`

## Current-master evidence
- current `master` still carries this slice note, the survey note, the raw-read fallback catalog, `zigux/tests/fixtures/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `scripts/zigux/check-phase12-virtio-scsi-packet.py`, `zigux/tests/phase12_build.zig`, and `zigux/Makefile`
- current `master` no longer serves `drivers/scsi/virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`, or `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig`
- `zigux/tests/phase12_build.zig` still acts as a shared Phase 12 support-bundle surface only: current `master` wires the `virtio_net` queue-resume, receive-refill replay, transmit-recycle, post-reset replay, throughput-parity, and survey-gate tests through the shared `smoke` and `test` steps, while the `virtio_scsi` lane is preserved here as rollback evidence only
- `scripts/zigux/check-phase12-virtio-scsi-packet.py` now fails closed if the survey packet stops matching this rollback-only current-master state

## Repo-reality boundaries
- the roadmap still places `drivers/scsi/virtio_scsi.c` in Phase 12 complex drivers, so DMA-safe abstractions, queueing correctness, throughput and recovery parity, and segmented rollout remain required before any honest live-storage claim
- `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` is an archival, commit-pinned raw-read companion and must not be treated as proof that current `master` still ships the direct replay family
- this slice is therefore rollback evidence only until the driver-local starter or its replay gates return to current `master`

## Why this packet exists
- the highest-value same-lane move is to keep the survey, fixture, and checker surfaces honest about the rollback-only state instead of widening into speculative driver work
- that keeps the Phase 12 lane reviewable without pretending that `scsi_host` lifecycle, blk-mq mapping, runtime queue ownership, DMA-backed request flow, or transport-backed recovery replay have landed

## Next bounded step
- leave the lane parked unless current `master` regains one bounded `virtio_scsi` driver-local file; if that happens, rebuild the survey packet around that returned surface before widening into runtime storage work