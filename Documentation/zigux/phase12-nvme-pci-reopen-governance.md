# Phase 12 NVMe PCI Reopen Governance

This note is the driver-local owner-map companion for the bounded Phase 12 `nvme_pci` packet.

It records when the current NVMe starter should reopen, who owns the reopen vocabulary, and which changes still stay outside the shared Phase 12 release packet.

It is a PMO and coordination artifact only. It does not add a new replay route.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_SLICE=nvme-pci-reopen-governance`
- `PHASE12_LANE=P12-L08`
- verified on: `2026-05-26`
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
  - `zigux/tests/phase12_nvme_pci_build.zig`
  - `zigux/tests/phase12_nvme_pci_survey_build.zig`
  - `zigux/tests/phase12_nvme_pci_manifest.json`
  - `zigux/tests/phase12_nvme_pci_survey.zig`
  - `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
  - `Documentation/zigux/phase12-nvme-pci-slice.md`
  - `Documentation/zigux/phase12-nvme-pci-survey.md`
  - `zigux/Makefile`

## Current Reopen Posture

- The current `nvme_pci` packet is real, deliberately driver-local, and still keeps one bounded direct replay through the dedicated `phase12-nvme-pci-direct-test` route in `zigux/tests/phase12_nvme_pci_build.zig` plus one bounded survey rerun through the dedicated `phase12-nvme-pci-survey-test` route in `zigux/tests/phase12_nvme_pci_survey_build.zig`, while keeping the survey gate itself packet-local beside the manifest and survey note.
- Current `master` now exposes `make -C zigux phase12-nvme-pci-direct-test` and `make -C zigux phase12-nvme-pci-survey-test` as dedicated wrapper handles for those two bounded reruns without widening the shared Phase 12 smoke-first packet.
- The shipped starter now keeps queue-pair planning, IO queue reservation sizing, recovery reservation replay preflight, PRP buffer-shape accounting, PRP metadata budgeting, stale PRP metadata ownership and descriptor-rebuild governance, dropped-backlog retirement review, rollback-gate review, and frozen queue-restore budgeting reviewable without claiming live DMA mapping, PRP or SGL construction, blk-mq submission, interrupt completion, timeout handling, or transport-backed reset replay.
- Cached PRP metadata from an older reset generation remains review-only debt. It can explain descriptor rebuild pressure, but it must not be treated as current-generation queue ownership until admin replay has completed and a current-generation rebuild replaces it.
- Current `master` does carry the direct replay, dedicated direct-build route, dedicated survey-build route, fallback map, slice note, survey note, survey gate, and manifest anchor for this bounded packet, while `zigux/tests/phase12_build.zig` still stays virtio_net-only.
- The reopen rule is therefore narrow: reopen this packet only when the bounded starter itself drifts, when the direct review packet, dedicated direct-build route, dedicated survey-build route, or dedicated make rerun wrappers drift, when the shared Phase 12 build route begins carrying NVMe, or when a later roadmap-backed transport-facing shard is explicitly proposed.

## Owner Split

- `P12-L08` owns the substantive driver-local NVMe starter packet in `drivers/nvme/host/pci.zig`, `drivers/nvme/host/pci_verify.zig`, `zigux/tests/phase12_nvme_pci.zig`, `zigux/tests/phase12_nvme_pci_build.zig`, `zigux/tests/phase12_nvme_pci_survey_build.zig`, `zigux/tests/phase12_nvme_pci_manifest.json`, `zigux/tests/phase12_nvme_pci_survey.zig`, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `zigux/Makefile`, and this owner-map note when those surfaces drift together, including the exact `cached_prp_metadata_stale` and `descriptor_rebuild_required` ownership vocabulary.
- `pmo-release` owns shared release wording in the Phase 12 sequencing, closure, readiness, and coordination notes.
- `complex-driver-shared-release-packet` owns the shared anti-overlap wording that keeps `virtio_net`, `virtio_scsi`, and the driver-local NVMe foothold distinct inside the same release packet.
- The current absence of NVMe from `zigux/tests/phase12_build.zig` is part of this note's truthfulness boundary, and any future shared-route expansion beyond the dedicated direct build, dedicated survey build, or dedicated make rerun wrappers should reopen this note together with the shared Phase 12 PMO packet.

## Reopen Triggers

Reopen this driver-local packet only if one of these conditions becomes true on current `master`:

1. The bounded starter changes its real surface.
   This includes new queue-reservation, recovery-replay, PRP metadata budgeting or ownership, dropped-backlog, rollback-gate, or frozen-restore-budget helpers in `drivers/nvme/host/pci.zig` or `drivers/nvme/host/pci_verify.zig`.

2. The driver-local review packet drifts.
   This includes changes to this owner map, the manifest in `zigux/tests/phase12_nvme_pci_manifest.json`, the direct replay in `zigux/tests/phase12_nvme_pci.zig`, the dedicated direct-build route in `zigux/tests/phase12_nvme_pci_build.zig`, the dedicated survey-build route in `zigux/tests/phase12_nvme_pci_survey_build.zig`, the dedicated `make -C zigux phase12-nvme-pci-direct-test` or `make -C zigux phase12-nvme-pci-survey-test` wrappers, or the coupled fallback, slice, survey, and survey-gate companions that describe the same bounded packet.

3. Shared replay wiring changes.
   If `zigux/tests/phase12_build.zig`, `zigux/Makefile`, or `.github/workflows/zigux-bootstrap.yml` begins wiring the current NVMe direct replay or any new NVMe coverage into the shared `phase12-smoke`, `phase12-test`, or `phase12` route, reopen this note together with the shared Phase 12 PMO packet.

4. A transport-facing shard is proposed.
   Reopen before landing any work that claims live DMA mapping, PRP or SGL construction, queue submission, interrupt-backed completion, timeout recovery, suspend or resume, or transport-backed reset replay.

## Non-Reopen Cases

- Do not reopen this note for reminder-only wording churn elsewhere in the docs root if the bounded NVMe packet itself has not changed.
- Do not reopen this note just because another Phase 12 driver packet moves.
- Do not treat public-read fallback maintenance alone as proof that the NVMe packet widened beyond its still-dedicated direct-build route.

## Boundaries

- This note must not promote the bounded NVMe starter beyond its current dedicated direct-build claim; the dedicated survey-build route, dedicated survey gate, dedicated make rerun wrappers, and broader runtime claims stay packet-local.
- This note must not translate stale PRP metadata ownership wording into a live DMA, PRP or SGL, or blk-mq ownership claim.
- This note must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.
- This note must not collapse the driver-local packet into a generic storage-delivery claim.

## Next Bounded Step

Leave the driver-local NVMe packet parked unless one exact same-family change lands first:

1. a bounded driver-local starter follow-up that still stays below live DMA and transport execution
2. one future shared-build wiring change that first introduces NVMe beyond the current dedicated direct-build route
3. one lane-local truthfulness repair if the manifest, owner map, direct replay, dedicated direct build, dedicated survey build, dedicated make rerun wrappers, coupled survey companions, or stale PRP ownership wording drift against the live packet