# Phase 12 NVMe PCI Raw GitHub Fallback Map

This note is the driver-local public-read fallback companion for the Phase 12 `nvme_pci` lane.

Current `master` does not materialize the direct NVMe PCI starter packet, so this file now serves as a repo-reality gap map instead of a commit-pinned direct replay index.

## Status
- `PHASE12_STATUS=active`
- `PHASE12_SLICE=nvme-pci-raw-github-fallback-map`
- `PHASE12_DIRECT_PACKET_ON_MASTER=absent`
- packet role: read-only driver-local gap inventory for degraded read workflows until a fresh bounded `nvme_pci` starter lands on current `master`
- release companions: `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`
- shared owner-map companion: `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
- driver-local owner-map companion: `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`
- verifier and replay companions that remain shipped today: `scripts/zigux/check-build-only-phase12-surface.py`, `zigux/tests/phase12_build.zig`, `zigux/Makefile`

## Current Master Gap Inventory
The following driver-local Phase 12 NVMe PCI paths are not materialized on current `master` and must be treated as repo-reality gaps until a bounded reland publishes them again:

- driver starter: `drivers/nvme/host/pci.zig`
- driver verifier: `drivers/nvme/host/pci_verify.zig`
- slice note: `Documentation/zigux/phase12-nvme-pci-slice.md`
- survey note: `Documentation/zigux/phase12-nvme-pci-survey.md`
- direct smoke replay: `zigux/tests/phase12_nvme_pci.zig`
- survey replay: `zigux/tests/phase12_nvme_pci_survey.zig`
- manifest anchor: `zigux/tests/phase12_nvme_pci_manifest.json`

The earlier commit pin recorded in this note no longer gives a trustworthy fallback route for those paths in the current accessible repository history, so it must not be reused as proof that the direct NVMe PCI packet is presently shipped on `master`.

## Review Use
- use this file only as a read-only gap inventory; it does not add a new replay surface
- keep this note aligned with the same smoke-first shared Phase 12 order already recorded in `Documentation/zigux/phase12-release-sequencing.md`
- keep the fallback split honest: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` remains a shipped commit-pinned fallback artifact, while this NVMe PCI note now records the direct packet as absent on current `master`
- rerun `python3 scripts/zigux/check-build-only-phase12-surface.py` before widening any PMO wording around the shared Phase 12 packet

## Boundaries
- this note must not imply a shared `validate-phase12.py`, `check-phase12-*.py`, focused `nvme_pci`-only replay, cross-build replay, or `phase12-validate` route that current `master` does not ship
- this note must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`
- this note must not present the absent direct NVMe PCI driver, verifier, survey, or manifest files as current shipped evidence

## Next Bounded Step
If this lane reopens, keep it to one bounded driver-local follow-up only:
- either reland one reviewable direct NVMe PCI starter packet covering `drivers/nvme/host/pci.zig`, `drivers/nvme/host/pci_verify.zig`, `zigux/tests/phase12_nvme_pci.zig`, `zigux/tests/phase12_nvme_pci_survey.zig`, and `zigux/tests/phase12_nvme_pci_manifest.json`
- or keep the lane parked on driver-local truthfulness surfaces until that bounded reland is ready
