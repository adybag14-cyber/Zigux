# Phase 12 NVMe PCI Raw GitHub Fallback Map

This note is the driver-local public-read fallback companion for the Phase 12 `nvme_pci` lane.

Current `master` now materializes the bounded NVMe PCI starter `drivers/nvme/host/pci.zig` together with the verifier shard `drivers/nvme/host/pci_verify.zig`, so this file must track the still-missing survey, slice, and replay surfaces without pretending the whole NVMe packet is absent.

## Status
- `PHASE12_STATUS=active`
- `PHASE12_SLICE=nvme-pci-raw-github-fallback-map`
- `PHASE12_DIRECT_PACKET_ON_MASTER=starter_and_verifier_shards_present_replays_absent`
- packet role: read-only driver-local gap inventory for degraded read workflows while the bounded starter plus verifier shards are shipped but the direct survey, slice, and replay companions remain outside the wired shared release packet
- release companions: `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`
- shared owner-map companion: `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
- driver-local owner-map companion: `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`
- starter, verifier, and shared replay companions that remain shipped today: `drivers/nvme/host/pci.zig`, `drivers/nvme/host/pci_verify.zig`, `scripts/zigux/check-build-only-phase12-surface.py`, `zigux/tests/phase12_build.zig`, `zigux/Makefile`

## Current Master Shipped Foothold
Current `master` now ships two bounded NVMe reviewability shards:

- starter shard: `drivers/nvme/host/pci.zig`
- verifier shard: `drivers/nvme/host/pci_verify.zig`

The starter shard keeps queue-planning, PRP buffer-shape, and reset-summary bookkeeping reviewable through the public tree, and the verifier shard keeps that bounded contract exercised. Those shipped shards still sit below a full direct NVMe replay packet because the slice, survey, and direct replay surfaces remain absent on current `master`.

## Current Master Gap Inventory
The following driver-local Phase 12 NVMe PCI paths are still not materialized on current `master` and must be treated as repo-reality gaps until a bounded reland publishes them again:

- slice note: `Documentation/zigux/phase12-nvme-pci-slice.md`
- survey note: `Documentation/zigux/phase12-nvme-pci-survey.md`
- direct smoke replay: `zigux/tests/phase12_nvme_pci.zig`
- survey replay: `zigux/tests/phase12_nvme_pci_survey.zig`
- manifest anchor: `zigux/tests/phase12_nvme_pci_manifest.json`

The earlier commit pin recorded in this note no longer gives a trustworthy fallback route for those still-missing slice, survey, and replay paths in the current accessible repository history, so it must not be reused as proof that the broader direct NVMe packet is already wired on `master`.

## Review Use
- use this file only as a read-only gap inventory; it does not add a new replay surface
- keep this note aligned with the same smoke-first shared Phase 12 order already recorded in `Documentation/zigux/phase12-release-sequencing.md`
- keep the fallback split honest: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` remains a shipped commit-pinned fallback artifact, while this NVMe PCI note now records the starter plus verifier shards as present and the still-missing survey, slice, and replay packet as absent on current `master`
- rerun `python3 scripts/zigux/check-build-only-phase12-surface.py` before widening any PMO wording around the shared Phase 12 packet

## Boundaries
- this note must not imply a shared `validate-phase12.py`, `check-phase12-*.py`, focused `nvme_pci`-only replay, cross-build replay, or `phase12-validate` route that current `master` does not ship
- this note must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`
- this note must not present the still-missing direct NVMe PCI slice, survey, or manifest files as current shipped evidence, and it must not round the bounded starter-plus-verifier packet up into a fully wired direct replay claim

## Next Bounded Step
If this lane reopens, keep it to one bounded driver-local follow-up only:
- either pair the shipped starter plus verifier shards with one reviewable direct NVMe PCI slice, survey, smoke replay, survey replay, and manifest packet
- or keep the lane parked on driver-local truthfulness surfaces until that bounded reland is ready
