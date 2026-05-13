# Phase 12 NVMe PCI Raw GitHub Fallback Map

This note is the driver-local public-read fallback companion for the Phase 12 `nvme_pci` lane.

Current `master` now materializes the bounded NVMe PCI starter `drivers/nvme/host/pci.zig` together with the verifier shard `drivers/nvme/host/pci_verify.zig`, the direct replay `zigux/tests/phase12_nvme_pci.zig`, the survey note `Documentation/zigux/phase12-nvme-pci-survey.md`, and the manifest anchor `zigux/tests/phase12_nvme_pci_manifest.json`, so this file must track the still-missing slice and survey-replay surfaces without pretending the whole NVMe packet is absent.

## Status
- `PHASE12_STATUS=active`
- `PHASE12_SLICE=nvme-pci-raw-github-fallback-map`
- `PHASE12_DIRECT_PACKET_ON_MASTER=starter_verifier_direct_replay_survey_note_and_manifest_present_survey_packet_incomplete`
- packet role: read-only driver-local gap inventory for degraded read workflows while the bounded starter, verifier, direct replay, survey note, and manifest anchor are shipped but the slice and survey-gate companions remain outside the wired shared release packet
- release companions: `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`
- shared owner-map companion: `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
- driver-local owner-map companion: `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`
- starter, verifier, direct replay, survey note, manifest, and shared replay companions that remain shipped today: `drivers/nvme/host/pci.zig`, `drivers/nvme/host/pci_verify.zig`, `zigux/tests/phase12_nvme_pci.zig`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `zigux/tests/phase12_nvme_pci_manifest.json`, `scripts/zigux/check-build-only-phase12-surface.py`, `zigux/tests/phase12_build.zig`, `zigux/Makefile`

## Current Master Shipped Foothold
Current `master` now ships five bounded NVMe reviewability surfaces:

- starter shard: `drivers/nvme/host/pci.zig`
- verifier shard: `drivers/nvme/host/pci_verify.zig`
- direct replay: `zigux/tests/phase12_nvme_pci.zig`
- survey note: `Documentation/zigux/phase12-nvme-pci-survey.md`
- manifest anchor: `zigux/tests/phase12_nvme_pci_manifest.json`

The starter shard keeps queue-planning, PRP buffer-shape, and reset-summary bookkeeping reviewable through the public tree, the verifier shard keeps that bounded contract exercised beside the driver, the direct replay keeps the queue-planner and PRP-shape starter reachable without claiming shared build wiring, the survey note keeps the roadmap-gap statement explicit beside the same shipped packet, and the manifest anchor records the current lane ownership plus blocked slice and survey-gate surfaces. Those shipped surfaces still sit below a full direct NVMe replay packet because the slice and survey-gate companions remain absent on current `master`.

## Current Master Gap Inventory
The following driver-local Phase 12 NVMe PCI paths are still not materialized on current `master` and must be treated as repo-reality gaps until a bounded reland publishes them again:

- slice note: `Documentation/zigux/phase12-nvme-pci-slice.md`
- survey replay: `zigux/tests/phase12_nvme_pci_survey.zig`

The earlier commit pin recorded in this note no longer gives a trustworthy fallback route for those still-missing slice and survey-gate paths in the current accessible repository history, so it must not be reused as proof that the broader direct NVMe packet is already wired on `master`.

## Review Use
- use this file only as a read-only gap inventory; it does not add a new replay surface
- keep this note aligned with the same smoke-first shared Phase 12 order already recorded in `Documentation/zigux/phase12-release-sequencing.md`
- keep the fallback split honest: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` remains a shipped commit-pinned fallback artifact, while this NVMe PCI note now records the starter, verifier, direct replay, survey note, and manifest anchor as present and the still-missing slice and survey-gate packet as absent on current `master`
- rerun `python3 scripts/zigux/check-build-only-phase12-surface.py` before widening any PMO wording around the shared Phase 12 packet

## Boundaries
- this note must not imply a shared `validate-phase12.py`, `check-phase12-*.py`, focused `nvme_pci`-only replay, cross-build replay, or `phase12-validate` route that current `master` does not ship
- this note must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`
- this note must not present the still-missing direct NVMe PCI slice or survey-gate files as current shipped evidence, and it must not round the bounded starter, verifier, direct replay, survey note, and manifest anchor up into a fully wired shared replay claim

## Next Bounded Step
If this lane reopens, keep it to one bounded driver-local follow-up only:
- either pair the shipped starter, verifier, direct replay, survey note, and manifest anchor with the still-missing direct NVMe PCI slice and survey replay packet
- or keep the lane parked on driver-local truthfulness surfaces until that bounded reland is ready