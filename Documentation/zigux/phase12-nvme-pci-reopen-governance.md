# Phase 12 NVMe PCI Reopen Governance

This note is the driver-local owner-map companion for the bounded Phase 12 `nvme_pci` packet.

It records when the current NVMe starter should reopen, who owns the reopen vocabulary, and which changes still stay outside the shared Phase 12 release packet.

It is a PMO and coordination artifact only. It does not add a new replay route.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_SLICE=nvme-pci-reopen-governance`
- `PHASE12_LANE=P12-L08`
- verified on: `2026-05-18`
- inspected branch: `master`
- roadmap anchor: `drivers/nvme/host/pci.c`
- shared PMO companions:
  - `Documentation/zigux/phase12-release-sequencing.md`
  - `Documentation/zigux/phase12-release-closure-checklist.md`
  - `Documentation/zigux/phase12-release-readiness-survey.md`
  - `Documentation/zigux/phase12-release-coordination-matrix.md`
- driver-local packet companions:
  - `drivers/nvme/host/pci.zig`
  - `drivers/nvme/host/pci_verify.zig`
  - `zigux/tests/phase12_nvme_pci.zig`
  - `zigux/tests/phase12_nvme_pci_manifest.json`

## Current Reopen Posture

- The current `nvme_pci` packet is real, but deliberately driver-local and still outside the shared `phase12-smoke` and `phase12` replay route.
- The shipped starter now keeps queue-pair planning, IO queue reservation sizing, recovery reservation replay preflight, PRP buffer-shape accounting, PRP metadata budgeting, dropped-backlog retirement review, rollback-gate review, and frozen queue-restore budgeting reviewable without claiming live DMA mapping, PRP or SGL construction, blk-mq submission, interrupt completion, timeout handling, or transport-backed reset replay.
- The reopen rule is therefore narrow: reopen this packet only when the bounded starter itself drifts, when the shared Phase 12 build route changes, or when a later roadmap-backed transport-facing shard is explicitly proposed.

## Owner Split

- `P12-L08` owns the substantive driver-local NVMe starter packet in `drivers/nvme/host/pci.zig`, `drivers/nvme/host/pci_verify.zig`, and `zigux/tests/phase12_nvme_pci.zig`.
- `P12-L10` owns driver-local truthfulness repairs for this owner map and any closely coupled fallback or review-note wording tied to the same bounded packet.
- `pmo-release` owns shared release wording in the Phase 12 sequencing, closure, readiness, and coordination notes.
- `complex-driver-shared-release-packet` owns the shared anti-overlap wording that keeps `virtio_net`, `virtio_scsi`, and the driver-local NVMe foothold distinct inside the same release packet.
- The shared build route remains outside this note's ownership until `zigux/tests/phase12_build.zig` or `zigux/Makefile` actually wires the NVMe direct replay into the shared smoke-first path.

## Reopen Triggers

Reopen this driver-local packet only if one of these conditions becomes true on current `master`:

1. The bounded starter changes its real surface.
   This includes new queue-reservation, recovery-replay, PRP metadata, dropped-backlog, rollback-gate, or frozen-restore-budget helpers in `drivers/nvme/host/pci.zig` or `drivers/nvme/host/pci_verify.zig`.

2. The driver-local review packet drifts.
   This includes changes to this owner map, the direct replay in `zigux/tests/phase12_nvme_pci.zig`, the manifest in `zigux/tests/phase12_nvme_pci_manifest.json`, or any surviving driver-local fallback or review note that describes the same bounded packet.

3. Shared replay wiring changes.
   If `zigux/tests/phase12_build.zig`, `zigux/Makefile`, or `.github/workflows/zigux-bootstrap.yml` begins wiring the NVMe direct replay into the shared `phase12-smoke`, `phase12-test`, or `phase12` route, reopen this note together with the shared Phase 12 PMO packet.

4. A transport-facing shard is proposed.
   Reopen before landing any work that claims live DMA mapping, PRP or SGL construction, queue submission, interrupt-backed completion, timeout recovery, suspend or resume, or transport-backed reset replay.

## Non-Reopen Cases

- Do not reopen this note for reminder-only wording churn elsewhere in the docs root if the bounded NVMe packet itself has not changed.
- Do not reopen this note just because another Phase 12 driver packet moves.
- Do not treat public-read fallback maintenance alone as proof that the NVMe packet entered the shared smoke-first route.

## Boundaries

- This note must not promote the bounded NVMe starter into a shared replay claim while `zigux/tests/phase12_build.zig` still leaves it unwired.
- This note must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.
- This note must not collapse the driver-local packet into a generic storage-delivery claim.

## Next Bounded Step

Leave the driver-local NVMe packet parked unless one exact same-family change lands first:

1. a bounded driver-local starter follow-up that still stays below live DMA and transport execution
2. one shared-build wiring change that makes NVMe part of the shared smoke-first Phase 12 route
3. one PMO truthfulness repair if the shared release packet drifts against this owner map
