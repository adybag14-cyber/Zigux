# Phase 12 NVMe PCI Survey

This note restores the bounded survey packet for `drivers/nvme/host/pci.c` on current `master`.

## Status

- `PHASE12_STATUS=starter_verifier_direct_replay_manifest_and_survey_gate_present_dedicated_build_present_shared_build_absent`
- `PHASE12_SLICE=nvme-pci-survey`
- lane owner: `P12-L08`
- roadmap anchor: `drivers/nvme/host/pci.c`
- current packet pin carried by the manifest: `ecc0463de6609349d805eb2a87fab7c7f72d3d4e`
- repo-truth boundary:
  - `Documentation/zigux/phase12-nvme-pci-survey.md`
  - `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
  - `Documentation/zigux/phase12-nvme-pci-slice.md`
  - `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`
  - `zigux/tests/phase12_nvme_pci_manifest.json`
  - `zigux/tests/phase12_nvme_pci_survey.zig`
  - `zigux/tests/phase12_nvme_pci_survey_build.zig`
  - `zigux/tests/phase12_nvme_pci.zig`
  - `zigux/Makefile`

## Current-master verification

- current `master` carries `drivers/nvme/host/pci.zig`
- current `master` carries `drivers/nvme/host/pci_verify.zig`
- current `master` carries `zigux/tests/phase12_nvme_pci_manifest.json`
- current `master` carries `zigux/tests/phase12_nvme_pci_build.zig`
- current `master` carries `zigux/tests/phase12_nvme_pci_survey_build.zig`
- current `master` carries `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`
- current `master` now exposes `make -C zigux phase12-nvme-pci-direct-test` and `make -C zigux phase12-nvme-pci-survey-test` as dedicated rerun wrappers for the existing driver-local direct replay and packet-local survey gate
- the shared `zigux/tests/phase12_build.zig` route still stays virtio-net-only, so the bounded NVMe packet remains driver-local through the dedicated `phase12-nvme-pci-direct-test` route in `zigux/tests/phase12_nvme_pci_build.zig` and the dedicated `phase12-nvme-pci-survey-test` route in `zigux/tests/phase12_nvme_pci_survey_build.zig`; the survey gate still stays packet-local beside the manifest and survey note
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
- one dedicated direct replay route for the bounded NVMe packet
- one dedicated survey-build route for the bounded NVMe survey gate
- one dedicated make rerun route for each of those two driver-local checks

The current bounded packet still does not prove:

- live DMA mapping
- PRP or SGL construction
- blk-mq submission ownership
- interrupt-backed completion handling
- transport-backed reset replay
- throughput evidence

## Why this survey matters

The manifest already claims that the survey note and dedicated survey gate are present. Keeping the note aligned with the still-dedicated direct replay, the dedicated survey-build rerun, the new dedicated make rerun wrappers, and the live stale-PRP ownership vocabulary keeps the packet fail-closed again, so the roadmap gap stays explicit instead of splitting across stale shared-route wording.

## Next bounded step

If the NVMe packet moves again, keep the next step inside the same driver-local boundary:

1. refresh the survey note, survey gate, and manifest together
2. repair one bounded direct replay, dedicated build, dedicated survey build, dedicated make rerun route, or verifier drift if it appears
3. leave shared-route promotion, throughput evidence, and live transport execution to their own later Phase 12 follow-up lane