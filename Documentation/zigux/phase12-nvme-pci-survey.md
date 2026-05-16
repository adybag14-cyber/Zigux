# Phase 12 NVMe PCI Survey

This note records the current-master verification result for the bounded Phase 12 lane around `drivers/nvme/host/pci.c`.

## Status

- `PHASE12_STATUS=starter-present-slice-note-survey-packet`
- `PHASE12_SLICE=nvme-pci-roadmap-gap-survey`
- `PHASE12_LANE=P12-L08`
- scope: verify the bounded `nvme_pci` Zig starter around queue-pair planning, controller-versus-planner I/O queue-count negotiation, PRP buffer-shape accounting, reset summaries, queue restart review, dropped-backlog retirement review, rollback-gate review, verifier-backed starter checks, frozen queue-restore budgeting, and the driver-local slice packet without widening into live DMA mapping, PRP or SGL construction, blk-mq submission, interrupt routing, or transport-backed reset recovery
- verified on: `2026-05-16`
- inspected head: `b3d7bdc604376af1f5412bec866dc7d36d7850c3`
- repo-truth boundary:
  - `drivers/nvme/host/pci.zig`
  - `drivers/nvme/host/pci_verify.zig`
  - `drivers/nvme/host/pci_queue_count.zig`
  - `zigux/tests/phase12_nvme_pci.zig`
  - `zigux/tests/phase12_nvme_pci_queue_count.zig`
  - `zigux/tests/phase12_nvme_pci_survey.zig`
  - `Documentation/zigux/phase12-nvme-pci-slice.md`
  - `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
  - `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`
  - `Documentation/zigux/phase12-nvme-pci-survey.md`
  - `zigux/tests/phase12_nvme_pci_manifest.json`

## Why this lane still matters

The Phase 12 roadmap still names `drivers/nvme/host/pci.c` as a complex production-driver target.

That anchor remains high value because `pci.c` still covers controller bring-up, queue provisioning, DMA-backed PRP or SGL submission, interrupt-driven completion, timeout recovery, and reset sequencing. The roadmap therefore still requires DMA-safe abstractions, queueing correctness, throughput and recovery parity, and segmented rollout before any honest live-NVMe claim.

## Current-master verification

- current `master` now carries `drivers/nvme/host/pci.zig`
- the current bounded starter exposes queue-pair planning, PRP buffer-shape accounting, reset summaries, queue restart review, dropped-backlog retirement review, rollback-gate review, and frozen queue-restore budgeting so those storage-driver boundaries stay reviewable without claiming live PCI transport or queue creation
- current `master` now carries `drivers/nvme/host/pci_queue_count.zig`, and that helper exposes `planIoQueueCount()` so controller queue caps, remaining planner slots, selected I/O queue count, queue-id window, total queue-pair count, and reset-generation visibility stay reviewable below live queue creation
- current `master` now carries `drivers/nvme/host/pci_verify.zig` as the bounded verifier shard for descriptor truthfulness, queue budgeting, PRP span pressure, queue restart review, rollback-gate ordering, and reset-state boundaries
- current `master` now carries `zigux/tests/phase12_nvme_pci.zig` as the direct bounded replay for the queue planner, queue restart summary, dropped-backlog retirement summary, rollback-gate summary, and PRP-shape starter
- current `master` now carries `zigux/tests/phase12_nvme_pci_queue_count.zig` as the direct bounded replay for the new queue-count helper
- current `master` now carries `zigux/tests/phase12_nvme_pci_manifest.json` as the lane-local roadmap-gap manifest
- current `master` now carries `zigux/tests/phase12_nvme_pci_survey.zig` as the dedicated survey gate for the NVMe packet
- current `master` now carries `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, and `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`, so the bounded starter-plus-verifier support packet is now explicit through driver-local notes as well as the survey surfaces
- current `master` still does not wire the bounded NVMe direct replay into `zigux/tests/phase12_build.zig` or the shared `phase12-smoke` and `phase12` routes

Those checks mean the current lane now has a truthful slice note and survey note for the existing NVMe starter packet plus the new queue-count helper, while the existing manifest and survey gate still cover the broader NVMe packet without yet naming the helper directly. The packet is still intentionally below any live DMA-backed queue execution, timeout recovery, or transport-backed reset claim.

## Truthful boundary

The truthful current boundary is:

- the roadmap still wants a bounded `nvme_pci` lane in Phase 12
- current `master` now carries `drivers/nvme/host/pci.zig`, and the current starter keeps queue-pair sizing, host-DMA budgeting, PRP buffer-shape pressure, reset freeze state, frozen queue-restore budgeting, queue-restart review, dropped-backlog retirement conditions, and rollback-gate review explicitly reviewable
- current `master` now carries `drivers/nvme/host/pci_queue_count.zig`, so controller-versus-planner I/O queue-count negotiation is also explicitly reviewable below live queue creation
- current `master` now carries the bounded verifier shard, the direct replay, the queue-count direct replay, the manifest anchor, the slice note, the fallback map, the reopen-governance note, this survey note, and the dedicated survey gate, so the starter is directly reviewable through driver-local surfaces even though the manifest and survey gate still summarize the broader packet
- current `master` still does not claim live DMA mapping, PRP or SGL construction, queue submission, blk-mq wiring, interrupt completion, timeout handling, suspend or resume, or transport-backed reset replay
- current `master` still does not claim shared Phase 12 build wiring, throughput parity, or measured recovery parity for the NVMe packet

## Non-goals

This note does not claim:

- a current live DMA mapping path
- a current PRP or SGL construction path
- a current blk-mq request submission or completion path
- a current interrupt, timeout, or suspend-resume path
- a current throughput benchmark or measured recovery parity result

## Next bounded step

The next honest same-lane move is now an exact reviewability refresh, not a transport-heavy implementation jump.

The next bounded step is:

1. keep the current starter focused on queue-pair planning, controller-versus-planner I/O queue-count negotiation, PRP buffer-shape accounting, reset summaries, queue restart review, dropped-backlog retirement review, rollback-gate review, verifier-backed checks, and frozen queue-restore budgeting instead of widening into live DMA or runtime PCI work
2. keep the survey note, manifest, and dedicated survey gate aligned if this packet drifts again, instead of widening into shared build wiring or runtime PCI work
3. treat shared build wiring, throughput parity, and recovery parity as blocked until later roadmap-backed abstractions land elsewhere

Until then, treat the current `nvme_pci` starter as a real but deliberately small Phase 12 survey packet, not as a live storage-driver proof.
