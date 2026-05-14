# Phase 12 NVMe PCI Survey

This note records the current-master verification result for the bounded Phase 12 lane around `drivers/nvme/host/pci.c`.

## Status

- `PHASE12_STATUS=starter-present-direct-replay-survey-note-and-gate`
- `PHASE12_SLICE=nvme-pci-roadmap-gap-survey`
- `PHASE12_LANE=P12-L08`
- scope: verify the bounded `nvme_pci` Zig starter around queue-pair planning, PRP buffer-shape accounting, reset summaries, dropped-backlog retirement review, verifier-backed starter checks, and frozen queue-restore budgeting without widening into live DMA mapping, PRP or SGL construction, blk-mq submission, interrupt routing, or transport-backed reset recovery
- verified on: `2026-05-14`
- repo-truth boundary:
  - `drivers/nvme/host/pci.zig`
  - `drivers/nvme/host/pci_verify.zig`
  - `zigux/tests/phase12_nvme_pci.zig`
  - `zigux/tests/phase12_nvme_pci_survey.zig`
  - `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
  - `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`
  - `Documentation/zigux/phase12-nvme-pci-survey.md`
  - `zigux/tests/phase12_nvme_pci_manifest.json`

## Why this lane still matters

The Phase 12 roadmap still names `drivers/nvme/host/pci.c` as a complex production-driver target.

That anchor remains high value because `pci.c` still covers controller bring-up, queue provisioning, DMA-backed PRP or SGL submission, interrupt-driven completion, timeout recovery, and reset sequencing. The roadmap therefore still requires DMA-safe abstractions, queueing correctness, throughput and recovery parity, and segmented rollout before any honest live-NVMe claim.

## Current-master verification

- current `master` now carries `drivers/nvme/host/pci.zig`
- the current bounded starter exposes `planAdminQueue()` and `planIoQueue()` so queue-pair sizing, host-DMA budgeting, and doorbell placement stay reviewable without claiming live PCI transport or queue creation
- the current bounded starter also exposes `planPrpBufferShape()` so PRP span pressure and PRP-list pressure stay reviewable without constructing live PRP or SGL mappings
- the current bounded starter also exposes `beginReset()`, `completeReset()`, `recoverySummary()`, and `recoveryQueueRestoreSummary()` so reset freeze state, remembered admin depth, planned IO queue counts, and frozen queue-restore host-DMA budgeting stay reviewable without claiming transport-backed reset replay
- the current bounded starter also exposes `summarizeDroppedIoRetirement()` so dropped-backlog retirement conditions stay reviewable after reset without claiming runtime queue teardown or completion ownership
- current `master` now carries `drivers/nvme/host/pci_verify.zig` as the bounded verifier shard for descriptor truthfulness, queue budgeting, PRP span pressure, and reset-state boundaries
- current `master` now carries `zigux/tests/phase12_nvme_pci.zig` as the direct bounded replay for the queue planner, dropped-backlog retirement summary, and PRP-shape starter
- current `master` now carries `zigux/tests/phase12_nvme_pci_manifest.json` as the lane-local roadmap-gap manifest
- current `master` now carries `zigux/tests/phase12_nvme_pci_survey.zig` as the dedicated survey gate for the NVMe packet
- current `master` still carries `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`, so the bounded starter-plus-verifier packet remains explicit even while the broader slice note remains absent
- current `master` still does not carry `Documentation/zigux/phase12-nvme-pci-slice.md`
- current `master` still does not wire the bounded NVMe direct replay into `zigux/tests/phase12_build.zig` or the shared `phase12-smoke` and `phase12` routes

Those checks mean the current lane now has a truthful survey note, manifest, and survey gate for the existing NVMe starter packet, but it is still intentionally below any live DMA-backed queue execution, timeout recovery, or transport-backed reset claim.

## Truthful boundary

The truthful current boundary is:

- the roadmap still wants a bounded `nvme_pci` lane in Phase 12
- current `master` now carries `drivers/nvme/host/pci.zig`, and the current starter keeps queue-pair sizing, host-DMA budgeting, PRP buffer-shape pressure, dropped-backlog retirement conditions, reset freeze state, and frozen queue-restore budgeting reviewable
- current `master` now carries the bounded verifier shard, the direct replay, the manifest anchor, the fallback map, the reopen-governance note, this survey note, and the dedicated survey gate, so the starter is directly reviewable through driver-local surfaces
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

The next honest same-lane move is still a survey-packet follow-through, not a transport-heavy implementation jump.

The next bounded step is:

1. keep the current starter focused on queue-pair planning, PRP buffer-shape accounting, reset summaries, dropped-backlog retirement review, verifier-backed checks, and frozen queue-restore budgeting instead of widening into live DMA or runtime PCI work
2. pair the present survey note and survey gate with the still-missing `Documentation/zigux/phase12-nvme-pci-slice.md` before claiming a fuller direct NVMe review packet
3. treat shared build wiring, throughput parity, and recovery parity as blocked until later roadmap-backed abstractions land elsewhere

Until then, treat the current `nvme_pci` starter as a real but deliberately small Phase 12 survey packet, not as a live storage-driver proof.
