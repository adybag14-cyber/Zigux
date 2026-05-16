# Phase 12 nvme_pci Slice

- `PHASE12_SLICE=nvme-pci-roadmap-gap-support`
- reread against live `master` and the current `P12-L08` survey packet on `2026-05-14`
- refreshed against the current `P7-L08` queue-count helper follow-up on `2026-05-16`
- lane: `complex-drivers-infra`
- anchor: `drivers/nvme/host/pci.c`

## Shipped packet

- `drivers/nvme/host/pci.zig` is the current bounded NVMe PCI scaffold on `master`
- `drivers/nvme/host/pci_verify.zig` keeps queue-plan descriptors, PRP span pressure, queue-restart and rollback blocker ordering, dropped-backlog retirement gates, and reset-state boundaries reviewable beside the driver-local starter
- `drivers/nvme/host/pci_queue_count.zig` keeps controller-versus-planner I/O queue-count negotiation reviewable below live queue creation, including the selected count, queue-id window, total queue-pair count, cap source, and reset-generation visibility
- `zigux/tests/phase12_nvme_pci.zig` keeps queue-pair planning, PRP buffer-shape accounting, queue-restart review, dropped-backlog retirement review, rollback-gate review, and frozen queue-restore budgeting directly executable without claiming shared build wiring
- `zigux/tests/phase12_nvme_pci_queue_count.zig` keeps the new queue-count helper directly executable without claiming shared build wiring
- `Documentation/zigux/phase12-nvme-pci-survey.md`, `zigux/tests/phase12_nvme_pci_manifest.json`, and `zigux/tests/phase12_nvme_pci_survey.zig` now keep the roadmap-gap survey machine-checkable beside this support note
- `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-nvme-pci-reopen-governance.md` keep degraded-read routing and lane-local ownership explicit while the packet remains below the shared Phase 12 build route

## Repo-reality gaps

- `zigux/tests/phase12_build.zig` still does not wire the bounded NVMe direct replay into the shared `phase12-smoke` or `phase12` routes
- `zigux/Makefile` still does not name a dedicated NVMe replay route inside the shared Phase 12 smoke-first packet
- live DMA mapping, PRP or SGL construction, blk-mq request submission, interrupt routing, timeout handling, suspend or resume, throughput parity, and transport-backed reset replay are still absent on the surveyed head

## Why this packet exists

- The roadmap's complex-driver lane still wants a bounded `drivers/nvme/host/pci.c` packet before any honest live-storage claim
- `master` already ships a real NVMe PCI starter, verifier shard, direct replay, survey note, manifest anchor, and survey gate for the existing NVMe starter packet, so the highest-value same-lane move here is a queue-count helper that makes controller caps versus the starter's own queue-id window explicit without widening into transport-heavy runtime work
- this slice keeps queue sizing, controller-versus-planner queue-count negotiation, host-DMA budgeting, PRP span pressure, queue-restart review, dropped-backlog retirement review, rollback-gate review, and frozen queue-restore budgeting grouped as one reviewable support packet while shared build wiring and throughput or recovery parity stay explicitly blocked elsewhere
- This note intentionally stays scoped to the current NVMe PCI support packet and does not claim a live DMA-backed queue path, interrupt flow, or broader Phase 12 closure
