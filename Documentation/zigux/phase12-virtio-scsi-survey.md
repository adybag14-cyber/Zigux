# Phase 12 virtio_scsi survey

This survey keeps the current `virtio_scsi` review packet truthful on `master` after the latest visible recovery-state test landed.

## Survey scope

This note covers only the currently visible recovery-state replay that landed in commit `38df8cb8d298b24baa5b21fecf00aac76876834e` on `2026-05-10 12:02:33 UTC`.

It does not treat older or broader `virtio_scsi` packet claims as revalidated during this refresh.

## Current visible replay

The active visible evidence is `zigux/tests/phase12_virtio_scsi_recovery_state.zig`.

That replay currently proves all of the following together:

- `captureQueueDepthSummary()` records a clamped queue-depth summary before recovery work starts
- `restoreAfterTransportReset()` clears the stale queue-depth state before a later freeze
- `planQueueLayout(3, 0)` relays the queue state to a no-poll layout after restore
- a later `freezeForTransportReset()` snapshots the relaid `3` request queues and `0` poll queues instead of stale earlier values
- `recoveryQueuePlan()` matches the relaid queue counts and leaves `first_poll_queue_index` unset for the zero-poll layout
- `recoveryQueueDepthSummary()` stays unavailable until a fresh post-restore summary is captured

## Review guidance

When this replay changes, keep these points explicit:

- the proof is about queue-state recovery bookkeeping, not end-to-end transport completion
- the zero-poll relaid layout is intentional evidence, not an omitted edge case
- clearing the stale queue-depth summary after restore is part of the contract
- later freezes must snapshot the relaid state, not a pre-restore snapshot

## Current boundary note

During this refresh, the available GitHub content reads for the broader `virtio_scsi` packet surfaces that are referenced elsewhere in the docs and checklist returned `404 Not Found`, so this survey intentionally records only the recovery-state replay that was directly visible on current `master`.

That means this note should be read as a bounded truthfulness update, not as evidence that the full Phase 12 `virtio_scsi` survey, manifest, or shared build packet was revalidated end to end in this run.

## Next bounded step

Once the adjacent `virtio_scsi` survey, manifest, and shared build-route surfaces are readable again through the active repo tools, carry this same recovery-state contract into those packet surfaces and keep the broader Phase 12 release-facing notes aligned with it without widening into new DMA-backed or throughput claims.
