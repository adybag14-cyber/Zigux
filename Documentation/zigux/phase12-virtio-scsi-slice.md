# Phase 12 virtio_scsi slice

This note records the current visible `virtio_scsi` recovery-state slice on `master`.

## Roadmap anchor

- Phase: `Phase 12`
- Linux anchor: `drivers/scsi/virtio_scsi.c`
- Zigux destination family: `drivers/scsi/virtio_scsi.zig`
- Required Phase 12 posture: queueing correctness, recovery parity, and segmented rollout before broader transport claims

## Latest substantive driver progress

The latest visible same-family driver progress on `master` during this note refresh is commit `38df8cb8d298b24baa5b21fecf00aac76876834e` from `2026-05-10 12:02:33 UTC`, which added `zigux/tests/phase12_virtio_scsi_recovery_state.zig`.

Later visible commits on `2026-05-10` touched only `Documentation/zigux/phase11-live-surface-audit.md` and `Documentation/zigux/review-checklist.md`, so this note is intentionally scoped to that new `virtio_scsi` recovery-state replay rather than implying additional storage-driver packet growth.

## Current visible evidence

`zigux/tests/phase12_virtio_scsi_recovery_state.zig` exercises a bounded queue-lab recovery path:

- captures a queue-depth summary with a clamped synthetic can-queue value
- freezes transport state and performs a restore
- replans queue layout after restore with `3` request queues and `0` poll queues
- proves the next freeze snapshots the relaid queue counts instead of stale pre-restore values
- proves `recoveryQueuePlan()` reflects the relaid queue counts and that no first poll queue index survives the zero-poll layout
- proves `recoveryQueueDepthSummary()` is unavailable until a new summary is captured after restore

## What this slice does not claim

This current visible replay is still a lab-only queue-state proof.

It does not yet claim:

- `Scsi_Host` lifecycle parity
- blk-mq mapping parity
- DMA-backed transport parity
- end-to-end I/O completion parity
- throughput or timeout recovery parity beyond the bounded queue-state replay above

## Next bounded step

If the surrounding Phase 12 `virtio_scsi` packet files become readable and writable through the active repo surfaces again, the next same-family step should wire this replay into the shared survey, manifest, and build-route packet without widening into new transport or DMA work.

Until then, keep Phase 12 storage-driver notes truthful about the visible current-master evidence: a real recovery-state replay landed, but the broader `virtio_scsi` packet should not be overstated beyond that bounded queue-state proof.
