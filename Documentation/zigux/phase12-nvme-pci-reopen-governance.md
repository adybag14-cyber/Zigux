# Phase 12 NVMe PCI Reopen Governance

This note is the driver-local owner-map companion for the bounded Phase 12 `nvme_pci` packet.

## Current Reopen Posture

- The current `nvme_pci` packet is real, deliberately driver-local, and stays outside the shared `phase12-smoke`, `phase12-test`, and aggregate `phase12` route while keeping its direct replay and survey gate on dedicated reruns.
- Current `master` keeps `make -C zigux phase12-nvme-pci-direct-test` and `make -C zigux phase12-nvme-pci-survey-test` as the explicit wrapper handles for the verifier-backed direct packet and the packet-local survey gate.
- The shared `phase12_build.zig` route is intentionally narrower than this owner packet, and any future shared-route expansion into `nvme_pci` should reopen this note together with the shared Phase 12 PMO packet before claiming broader complex-driver coverage.

## Boundaries

- This note must not promote the bounded NVMe starter beyond its current dedicated direct replay, dedicated survey, verifier-backed foothold, and driver-local reminder claims.
- This note must not translate stale PRP metadata ownership wording into a live DMA, PRP or SGL, or blk-mq ownership claim.
- This note must not collapse the driver-local packet into a generic storage-delivery claim.
