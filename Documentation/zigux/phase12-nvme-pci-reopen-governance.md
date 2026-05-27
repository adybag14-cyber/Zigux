# Phase 12 NVMe PCI Reopen Governance

This note is the driver-local owner-map companion for the bounded Phase 12 `nvme_pci` packet.

## Current Reopen Posture

- The current `nvme_pci` packet is real, deliberately driver-local, and now shares one bounded direct replay through the shared `phase12-smoke`, `phase12-test`, and `phase12` routes while still keeping the verifier shard on the dedicated `phase12-nvme-pci-direct-test` route and the survey gate itself packet-local beside the manifest and survey note.
- Current `master` keeps `make -C zigux phase12-nvme-pci-direct-test` and `make -C zigux phase12-nvme-pci-survey-test` as dedicated wrapper handles for the verifier-backed direct packet and the packet-local survey gate.
- The current shared direct replay wiring in `zigux/tests/phase12_build.zig` is part of this note's truthfulness boundary, and any future shared-route expansion beyond that bounded direct replay should reopen this note together with the shared Phase 12 PMO packet.

## Boundaries

- This note must not promote the bounded NVMe starter beyond its current shared direct replay plus dedicated verifier and survey claims.
- This note must not translate stale PRP metadata ownership wording into a live DMA, PRP or SGL, or blk-mq ownership claim.
- This note must not collapse the driver-local packet into a generic storage-delivery claim.
