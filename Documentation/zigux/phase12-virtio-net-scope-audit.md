# Phase 12 Virtio Net Scope Audit

This note records one freeze-aware same-lane audit of the live `virtio_net` Phase 12 packet on `master`.

It is not a slice note, not a release-closure claim, and not a widening of the active driver boundary.

## Why this audit exists

The Phase 12 roadmap keeps `drivers/net/virtio_net.c` inside segmented preparation until Zigux has real DMA-safe abstractions, queueing correctness substrate work, and throughput plus recovery parity evidence.

The live survey-backed `virtio_net` packet is intentionally smaller than the Linux driver. That bounded packet is useful, but only if the repo keeps one truthful answer to the question "what is actually landed right now?"

Fresh repo inspection on 2026-05-10 showed one actionable drift point:

- `Documentation/zigux/phase12-complex-driver-lane-sequencing.md` currently describes the `virtio_net` live scope as including a repeated-recovery-cycle follow-up.
- `Documentation/zigux/phase12-virtio-net-survey.md` still describes the landed packet as the probe snapshot starter plus the syntax-lab, queue-recovery, receive-refill, control-queue-restore, transmit-recycle, and mergeable-buffer-length follow-ups, followed by the segmented rollout boundary.
- `zigux/tests/phase12_virtio_net_manifest.json` still records the same bounded packet and still treats the runtime data path as blocked below DMA-backed work.

That mismatch is small, but it matters because this lane is schedule-driven and easy to overclaim if the anti-overlap note gets ahead of the survey-backed source of truth.

## Live packet that this audit treats as landed

Until the driver, tests, manifest, and survey move together, treat the current `virtio_net` packet as:

- the probe snapshot starter in `drivers/net/virtio_net.zig`
- the direct syntax-lab reachability shard in `zigux/tests/phase12_virtio_net_syntax_lab.zig`
- the queue-recovery follow-up
- the receive-refill follow-up
- the control-queue-restore follow-up
- the transmit-recycle follow-up
- the mergeable-buffer-length follow-up
- the segmented rollout boundary that keeps the lane below live DMA-backed runtime data-path work

## Freeze and non-goal guard

This audit does not reopen or imply delivery against:

- `net/core/skbuff.c`
- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`
- NAPI poll loops
- page-pool or DMA-backed buffer ownership
- XDP or XSK execution paths
- control-virtqueue command traffic
- RSS table programming
- `net_device` lifecycle work

Those remain outside the active Phase 12 `virtio_net` packet unless the roadmap evidence and freeze-map status change first.

## Bounded next step

The next honest same-family move is one of these, but not both in a half-step:

1. Retire the repeated-recovery-cycle wording from the shared complex-driver lane note and any coupled shared summaries so the anti-overlap owner map matches the survey-backed packet again.
2. Land a real repeated-recovery-cycle follow-up across `drivers/net/virtio_net.zig`, the direct tests, the manifest, and the survey note in one packet, while keeping the work below live DMA, queue-execution, and transport-facing claims.

If neither happens, keep the survey note and manifest as the tighter boundary and treat the repeated-recovery wording as reopen drift rather than as landed scope.

## Grounding

This audit was written against:

- the Phase 12 roadmap section for complex production drivers and heavy helper consumers
- `Documentation/zigux/freeze-map.md`
- `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
- `Documentation/zigux/phase12-virtio-net-survey.md`
- `zigux/tests/phase12_virtio_net_manifest.json`
