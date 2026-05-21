# Phase 12 NVMe PCI Survey

This note restores the bounded survey packet for `drivers/nvme/host/pci.c` on current `master`.

## Status

- `PHASE12_STATUS=starter_verifier_direct_replay_manifest_and_survey_gate_present_shared_build_unwired`
- `PHASE12_SLICE=nvme-pci-survey`
- lane owner: `P12-L08`
- roadmap anchor: `drivers/nvme/host/pci.c`
- current packet pin carried by the manifest: `7f9b8703b96d4de67447791a88584023950b1de7`
- repo-truth boundary:
  - `Documentation/zigux/phase12-nvme-pci-survey.md`
  - `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
  - `Documentation/zigux/phase12-nvme-pci-slice.md`
  - `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`
  - `zigux/tests/phase12_nvme_pci_manifest.json`
  - `zigux/tests/phase12_nvme_pci_survey.zig`
  - `zigux/tests/phase12_nvme_pci.zig`

## Current-master verification

- current `master` carries `drivers/nvme/host/pci.zig`
- current `master` carries `drivers/nvme/host/pci_verify.zig`
- current `master` carries `zigux/tests/phase12_nvme_pci_manifest.json`
- current `master` carries `zigux/tests/phase12_nvme_pci_build.zig`
- current `master` carries `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`
- the bounded packet remains driver-local: `zigux/tests/phase12_build.zig` still does not wire the NVMe direct replay into the shared `phase12-smoke` or `phase12` routes
- the truthful runtime boundary is still below live DMA mapping, PRP or SGL construction, blk-mq request ownership, interrupt completion, timeout recovery, and transport-backed queue execution

## Roadmap gap versus current packet

The Phase 12 roadmap requires DMA-safe abstractions, queueing correctness, throughput and recovery parity, and segmented rollout before `drivers/nvme/host/pci.zig` can honestly widen into a deeper production-driver claim.

The current bounded packet only proves reviewability for:

- queue-pair planning and IO queue reservation sizing
- recovery reservation replay preflight and queue-numbering restart review
- PRP buffer-shape accounting and PRP metadata budgeting
- reset freeze summaries and frozen queue-restore host-DMA budgeting
- dropped-backlog retirement review
- rollback-gate review

The current bounded packet still does not prove:

- live DMA mapping
- PRP or SGL construction
- blk-mq submission ownership
- interrupt-backed completion handling
- transport-backed reset replay
- throughput evidence

## Why this survey matters

The manifest already claims that the survey note and survey gate are present. Restoring them keeps the packet fail-closed again, so the roadmap gap stays explicit instead of living only in the manifest text.

## Next bounded step

If the NVMe packet moves again, keep the next step inside the same driver-local boundary:

1. refresh the survey note, survey gate, and manifest together
2. repair one bounded direct replay or verifier drift if it appears
3. leave shared-build wiring and live transport execution to their own later Phase 12 follow-up lane
