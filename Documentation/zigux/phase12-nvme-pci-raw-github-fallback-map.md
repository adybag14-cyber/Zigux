# Phase 12 NVMe PCI Raw GitHub Fallback Map

This note records the bounded Phase 12 NVMe PCI packet that is directly inspectable on `master` even when a full repo checkout is unavailable.

## Status

- `PHASE12_DIRECT_PACKET_ON_MASTER=starter_verifier_slice_note_direct_replay_survey_note_survey_gate_and_manifest_present_shared_build_unwired`
- lane owner: `P12-L08`
- roadmap anchor: `drivers/nvme/host/pci.c`
- packet scope: keep the current NVMe PCI starter reviewable without claiming live DMA mapping, PRP or SGL submission, blk-mq wiring, or transport-backed queue execution

## Direct Packet

- starter shard: `drivers/nvme/host/pci.zig`
- verifier shard: `drivers/nvme/host/pci_verify.zig`
- direct replay: `zigux/tests/phase12_nvme_pci.zig`
- survey gate: `zigux/tests/phase12_nvme_pci_survey.zig`
- manifest anchor: `zigux/tests/phase12_nvme_pci_manifest.json`
- `zigux/tests/phase12_build.zig` still does not wire the bounded NVMe direct replay into the shared `phase12-smoke` or `phase12` routes

## Boundary

This fallback map is read-only evidence for the bounded starter packet. It does not claim that the NVMe replay is part of the shared smoke-first Phase 12 route.
