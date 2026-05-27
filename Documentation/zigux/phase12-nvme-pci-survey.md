# Phase 12 NVMe PCI Survey

This note restores the bounded survey packet for `drivers/nvme/host/pci.c` on current `master`.

## Status

- `PHASE12_STATUS=starter_verifier_direct_replay_manifest_and_survey_gate_present_shared_direct_replay_present`
- `PHASE12_SLICE=nvme-pci-survey`
- lane owner: `P12-L08`
- roadmap anchor: `drivers/nvme/host/pci.c`
- current packet pin carried by the manifest: `ecc0463de6609349d805eb2a87fab7c7f72d3d4e`

## Current-master verification

- current `master` carries `drivers/nvme/host/pci.zig`
- current `master` carries `drivers/nvme/host/pci_verify.zig`
- current `master` carries `zigux/tests/phase12_nvme_pci_manifest.json`
- current `master` carries `zigux/tests/phase12_nvme_pci_build.zig`
- current `master` carries `zigux/tests/phase12_nvme_pci_survey_build.zig`
- current `master` exposes `make -C zigux phase12-nvme-pci-direct-test` and `make -C zigux phase12-nvme-pci-survey-test` as dedicated rerun wrappers for the existing driver-local direct replay and packet-local survey gate
- the shared `zigux/tests/phase12_build.zig` route now wires the bounded NVMe direct replay into `phase12-smoke`, `phase12-test`, and `phase12`, while the verifier shard remains on the dedicated `phase12-nvme-pci-direct-test` route and the survey gate still stays packet-local beside the manifest and survey note
- the truthful runtime boundary is still below live DMA mapping, PRP or SGL construction, blk-mq request ownership, interrupt completion, timeout recovery, and transport-backed queue execution

## Roadmap gap versus current packet

The Phase 12 roadmap requires DMA-safe abstractions, queueing correctness, throughput and recovery parity, and segmented rollout before `drivers/nvme/host/pci.zig` can honestly widen into a deeper production-driver claim.

The current bounded packet only proves reviewability for:

- queue-pair planning and IO queue reservation sizing
- recovery reservation replay debt, preflight, apply, and queue-numbering restart review
- PRP buffer-shape accounting, PRP metadata budgeting, and stale PRP metadata ownership with descriptor-rebuild governance
- reset freeze summaries and frozen queue-restore host-DMA budgeting
- dropped-backlog retirement review
- rollback-gate review
- one dedicated survey-build route for the bounded NVMe survey gate
- one dedicated make rerun route for the survey gate
- one dedicated verifier-backed route for the helper-local wrapper packet
- one shared direct replay route for the bounded NVMe packet

The current bounded packet still does not prove:

- live DMA mapping
- PRP or SGL construction
- blk-mq submission ownership
- interrupt-backed completion handling
- transport-backed reset replay
- throughput evidence
