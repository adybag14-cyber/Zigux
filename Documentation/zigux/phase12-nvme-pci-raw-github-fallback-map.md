# Phase 12 NVMe PCI Raw GitHub Fallback Map

This note is the driver-local public-read fallback companion for the Phase 12 `nvme_pci` lane.

Current `master` now materializes the bounded NVMe PCI starter `drivers/nvme/host/pci.zig` together with the verifier shard `drivers/nvme/host/pci_verify.zig`, the direct replay `zigux/tests/phase12_nvme_pci.zig`, the slice note `Documentation/zigux/phase12-nvme-pci-slice.md`, the survey note `Documentation/zigux/phase12-nvme-pci-survey.md`, the survey gate `zigux/tests/phase12_nvme_pci_survey.zig`, and the manifest anchor `zigux/tests/phase12_nvme_pci_manifest.json`, so this file must track the still-blocked shared-build route without pretending the whole NVMe packet is absent.

## Status
- `PHASE12_STATUS=active`
- `PHASE12_SLICE=nvme-pci-raw-github-fallback-map`
- `PHASE12_DIRECT_PACKET_ON_MASTER=starter_verifier_slice_note_direct_replay_survey_note_survey_gate_and_manifest_present_shared_build_unwired`
- packet role: read-only driver-local inventory for degraded read workflows while the bounded starter, verifier, slice note, direct replay, survey note, survey gate, and manifest anchor are shipped but the shared build route remains outside the wired Phase 12 smoke packet
- release companions: `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`
- shared owner-map companion: `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
- driver-local owner-map companion: `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`
- starter, verifier, direct replay, slice note, survey note, survey gate, manifest, and shared replay companions that remain shipped today: `drivers/nvme/host/pci.zig`, `drivers/nvme/host/pci_verify.zig`, `zigux/tests/phase12_nvme_pci.zig`, `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `zigux/tests/phase12_nvme_pci_survey.zig`, `zigux/tests/phase12_nvme_pci_manifest.json`, `scripts/zigux/check-build-only-phase12-surface.py`, `zigux/tests/phase12_build.zig`, `zigux/Makefile`

## Current Master Shipped Foothold
Current `master` now ships seven bounded NVMe reviewability surfaces:

- starter shard: `drivers/nvme/host/pci.zig`
- verifier shard: `drivers/nvme/host/pci_verify.zig`
- direct replay: `zigux/tests/phase12_nvme_pci.zig`
- slice note: `Documentation/zigux/phase12-nvme-pci-slice.md`
- survey note: `Documentation/zigux/phase12-nvme-pci-survey.md`
- survey gate: `zigux/tests/phase12_nvme_pci_survey.zig`
- manifest anchor: `zigux/tests/phase12_nvme_pci_manifest.json`

The starter shard keeps queue planning, PRP buffer-shape accounting, queue restart review, dropped-backlog retirement review, rollback-gate review, and frozen queue-restore budgeting reviewable through the public tree, the verifier shard keeps descriptor truthfulness, blocker ordering, and reset-state boundaries exercised beside the driver, the direct replay keeps those same bounded queue-and-recovery summaries reachable without claiming shared build wiring, the slice note and survey note keep the roadmap-gap narrative explicit beside the same shipped packet, the survey gate keeps that packet machine-checkable, and the manifest anchor records the current lane ownership plus the still-blocked shared-build surface. Those shipped surfaces still sit below a shared Phase 12 smoke packet because `zigux/tests/phase12_build.zig` does not yet wire the NVMe direct replay into the smoke-first route.

## Current Master Gap Inventory
There are no remaining driver-local reminder-file gaps on current `master`. The still-open degraded-read gap is shared routing, not another absent NVMe packet file:

- `zigux/tests/phase12_build.zig` still does not wire the bounded NVMe direct replay into the shared `phase12-smoke` or `phase12` routes
- `zigux/Makefile` still does not advertise a dedicated NVMe replay route inside the smoke-first packet

## Review Use
- use this file only as a read-only routing inventory; it does not add a new replay surface
- keep this note aligned with the same smoke-first shared Phase 12 order already recorded in `Documentation/zigux/phase12-release-sequencing.md`
- keep the fallback split honest: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` remains a shipped commit-pinned fallback artifact, while this NVMe PCI note now records the full driver-local packet as present and the shared build route as still unwired on current `master`
- rerun `python3 scripts/zigux/check-build-only-phase12-surface.py` before widening any PMO wording around the shared Phase 12 packet

## Boundaries
- this note must not imply a shared `validate-phase12.py`, `check-phase12-*.py`, focused `nvme_pci`-only replay, cross-build replay, or `phase12-validate` route that current `master` does not ship
- this note must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`
- this note must not round the bounded starter, verifier, direct replay, slice note, survey note, survey gate, and manifest anchor up into a fully wired shared replay claim while the shared build route remains missing

## Next Bounded Step
If this lane reopens, keep it to one bounded driver-local follow-up only:
- either keep the shipped starter, verifier, direct replay, slice note, survey note, survey gate, and manifest anchor aligned while the shared build route stays blocked
- or leave the lane parked on driver-local truthfulness surfaces until a later shared-build packet is ready
