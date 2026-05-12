# Phase 12 Virtio SCSI Survey

This note records the current-master verification result for the bounded Phase 12 lane around `drivers/scsi/virtio_scsi.c`.

## Status

- `PHASE12_STATUS=starter-present-queue-and-recovery-survey`
- `PHASE12_SLICE=virtio-scsi-roadmap-gap-survey`
- scope: verify the bounded `virtio_scsi` Zig starter around queue layout, probe snapshot, host-limit, queue-depth, command-buffer ownership, io-map, and transport-reset recovery summaries without widening into live DMA-safe request flow, blk-mq execution, `scsi_host` registration, or transport-backed host-scan runtime work
- verified on: `2026-05-12`
- repo-truth boundary:
  - `drivers/scsi/virtio_scsi.zig`
  - `zigux/tests/phase12_virtio_scsi.zig`
  - `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`
  - `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`
  - `zigux/tests/phase12_virtio_scsi_packet.zig`
  - `zigux/tests/fixtures/phase12_virtio_scsi_manifest.json`
  - `scripts/zigux/check-phase12-virtio-scsi-packet.py`
  - `Documentation/zigux/phase12-virtio-scsi-slice.md`
  - `Documentation/zigux/phase12-virtio-scsi-survey.md`
  - `zigux/tests/phase12_virtio_scsi_manifest.json`
  - `zigux/tests/phase12_virtio_scsi_survey.zig`
  - `zigux/tests/phase12_build.zig`
  - `zigux/Makefile`

## Why this lane still matters

The Phase 12 roadmap still names `drivers/scsi/virtio_scsi.c` as a complex production-driver target.

That anchor remains high value because `virtio_scsi.c` still covers virtqueue setup, event handling, request submission, sense-buffer ownership, control commands, transport reset, and host-scan recovery sequencing. The roadmap therefore still requires DMA-safe abstractions, queueing correctness, throughput and recovery parity, and segmented rollout before any honest live-storage claim.

## Current-master verification

- current `master` now carries `drivers/scsi/virtio_scsi.zig`
- the current bounded starter exposes `planQueueLayout()`, `requestQueue()`, `captureProbeSnapshot()`, `captureHostLimitSummary()`, `captureQueueDepthSummary()`, `captureCommandBufferOwnershipSummary()`, and `captureIoQueueMapSummary()` so queue-family planning, host-limit clamping, queue-depth clamping, command and sense-buffer ownership planning, and io-map offsets stay reviewable without claiming live blk-mq traffic
- the current bounded starter also exposes `freezeForTransportReset()`, `recoveryQueuePlan()`, `recoveryQueueDepthSummary()`, `recoveryIoQueueMapSummary()`, `recoveryEventBufferOwnershipSummary()`, `recoveryHostScanSummary()`, and `restoreAfterTransportReset()` so transport-reset recovery order, event-buffer ownership, and host-scan restore ordering stay reviewable without claiming runtime reset execution
- current `master` now carries `zigux/tests/phase12_virtio_scsi.zig` as the direct bounded replay for this starter
- current `master` now carries `zigux/tests/phase12_virtio_scsi_syntax_lab.zig` as the dedicated syntax lab for this starter
- current `master` now carries `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig` so the second-cycle recovery boundary remains explicit
- current `master` now carries `zigux/tests/phase12_virtio_scsi_packet.zig`, `zigux/tests/fixtures/phase12_virtio_scsi_manifest.json`, `scripts/zigux/check-phase12-virtio-scsi-packet.py`, and `Documentation/zigux/phase12-virtio-scsi-slice.md` as the earlier support packet for this starter
- current `master` now carries this survey note plus `zigux/tests/phase12_virtio_scsi_manifest.json` and `zigux/tests/phase12_virtio_scsi_survey.zig` so the roadmap-gap survey is now machine-checkable beside the earlier support packet
- current `master` still carries `zigux/tests/phase12_build.zig`, and that shared build route still runs the direct `virtio_scsi` tests, syntax-lab smoke, repeated-replan gate, and packet replay
- `zigux/Makefile` still carries `phase12-smoke`, `phase12-test`, and `phase12`, and those shared routes continue to pick up the bounded `virtio_scsi` packet through `zigux/tests/phase12_build.zig`

Those checks mean the current lane now has a truthful survey packet for the existing `virtio_scsi` starter, but it is still intentionally below any live DMA-backed request path or runtime host integration claim.

## Truthful boundary

The truthful current boundary is:

- the roadmap still wants a bounded `virtio_scsi` lane in Phase 12
- current `master` now carries `drivers/scsi/virtio_scsi.zig`, and the current starter keeps queue layout, host-limit, queue-depth, command-buffer ownership, io-map, transport-reset, event-buffer ownership, and host-scan restore ordering reviewable
- current `master` now carries the direct test, syntax lab, repeated-replan gate, support packet, and this survey packet, so the starter is directly executable and reviewable through bounded driver-local surfaces
- current `master` still does not claim live DMA-safe request submission, sg-list ownership, request completion handling, blk-mq tag wiring, `scsi_host` registration, TMF execution, event-queue runtime handling, or transport-backed host-scan recovery
- current `master` still does not claim throughput parity, reset replay parity, or a live storage data path

## Non-goals

This note does not claim:

- a current live request submission path
- a current DMA-safe buffer ownership or sg-chain implementation
- a current blk-mq or `scsi_host` registration path
- a current transport-backed event, TMF, or host-scan execution path
- a current throughput benchmark or measured recovery parity result

## Next bounded step

The next honest same-lane move is a bounded request-submit sequencing follow-up, not a runtime storage-path jump.

The next bounded step is:

1. keep the current starter focused on queue layout, host-limit, queue-depth, command-buffer ownership, io-map, and transport-reset recovery summaries instead of widening into live DMA or host-registration code
2. reland one request-submit sequencing follow-up beside the current `virtio_scsi` starter so the next queue-facing contract becomes reviewable without overclaiming runtime behavior
3. revisit broader Phase 12 bundle wiring only after that follow-up exists and still fits the bounded complex-driver packet

Until then, treat the current `virtio_scsi` starter as a real but deliberately small Phase 12 queue-and-recovery survey packet, not as a live storage-driver proof.
