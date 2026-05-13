# Phase 12 virtio-net recovery governance note

This note records one bounded driver-local recovery-governance companion for `drivers/net/virtio_net.zig`.

It exists to keep the current post-reset handoff explicit without widening into live DMA, NAPI, XDP, XSK, control-virtqueue command traffic, RSS table programming, or full `net_device` lifecycle work.

## Scope

- `PHASE12_STATUS=driver-local-recovery-governance-note`
- `PHASE12_SLICE=virtio-net-recovery-governance-note`
- anchor: `drivers/net/virtio_net.c`
- direct driver surface: `drivers/net/virtio_net.zig`
- direct review gates:
  - `zigux/tests/phase12_virtio_net.zig`
  - `zigux/tests/phase12_virtio_net_syntax_lab.zig`
  - `Documentation/zigux/phase12-virtio-net-survey.md`

## Current bounded packet

The active `virtio_net` starter already keeps several recovery-facing surfaces reviewable in memory:

- `recoveryQueuePlan()` keeps the remembered receive, transmit, and optional control-queue topology explicit after a frozen reset snapshot.
- `controlQueueRecoveryPlan()` keeps control-state restore ordering explicit and marks when dirty control state must be restored before data queues can be treated as ready.
- `planControlQueuePayloadShape()` keeps receive-mode, hash-report, MAC, VLAN, and RSS payload bounds explicit before the lane claims any runtime control-virtqueue command execution.
- `restoreAfterReset()` closes the bounded cycle by clearing stale remembered state and incrementing the recovery generation.

## Governance order

Keep the current driver-local handoff in this order:

1. Freeze the bounded probe and queue state first so the remembered queue shape and refill expectations stop moving during the reset window.
2. Use `recoveryQueuePlan()` to decide which receive, transmit, and optional control queues still need restore work after that frozen snapshot.
3. If `controlQueueRecoveryPlan()` reports dirty control state, keep that control-queue restore governance ahead of the data-queue-ready claim for the same recovery generation.
4. Use `planControlQueuePayloadShape()` to bound the exact control payload footprint before treating receive-mode, hash-report, MAC, VLAN, or RSS restore intent as reviewable work.
5. Keep receive-refill follow-through subordinate to that remembered queue plan so mergeable-buffer expectations remain a gated post-reset dependency rather than an implied live refill loop.
6. Let `restoreAfterReset()` end the bounded governance cycle only after those remembered plans have been consumed and the next generation is ready to require a fresh probe snapshot.

## Boundaries

This note does not claim:

- live control-virtqueue traffic
- runtime data-queue execution
- DMA-safe receive ownership
- page-pool refill loops
- RSS table programming
- NAPI, XDP, or XSK behavior
- `net_device` open, close, suspend, resume, or teardown behavior

## Next bounded step

Reopen this note only if the driver-local packet adds a new post-reset owner, changes the control-versus-data restore ordering, or widens the payload-shaping surface.

Until then, keep this file as a small governance companion to the current bounded `virtio_net` recovery packet rather than a runtime-data-path claim.
