# Phase 12 NVMe PCI Survey

This survey note records the current bounded Phase 12 checkpoint around `drivers/nvme/host/pci.c`.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_LANE_KEY=P12-Y02`
- `PHASE12_SLICE=nvme-pci-survey`
- scope: archival survey manifest, dedicated survey gate, shared Phase 12 build and make-target wiring, and a lane note that compares the landed `pci.zig` starter against the remaining roadmap gap and the current Phase 12 tranche state
- owner lane: `P12-Y02`
- product boundary:
  - `drivers/nvme/host/pci.zig`
  - `zigux/tests/phase12_nvme_pci.zig`
  - `zigux/tests/phase12_nvme_pci_manifest.json`
  - `zigux/tests/phase12_nvme_pci_survey.zig`
  - `zigux/tests/phase12_build.zig`
  - `Documentation/zigux/phase12-nvme-pci-slice.md`
  - `Documentation/zigux/phase12-nvme-pci-survey.md`

## Why this slice exists

The Phase 12 roadmap explicitly names `drivers/nvme/host/pci.c` as a complex production-driver target, and the live repo now has a first bounded `drivers/nvme/host/pci.zig` starter.

That starter is real progress, but it is still only a narrow queue planner plus PRP helpers. The Linux anchor is 4,293 lines and mixes quirk parsing, admin-queue bring-up, MSI and MSI-X planning, blk-mq queue mapping, PRP and SGL setup, Host Memory Buffer controls, timeout and reset policy, PCI queue creation, completion polling, and suspend or teardown flows.

This survey keeps that difference explicit so the lane does not overclaim production-driver progress.

## Survey findings

- `drivers/nvme/host/pci.c` is present on `master` and remains a high-risk complex-driver anchor whose live behavior stretches far beyond the current Zigux starter.
- the live repo now ships `drivers/nvme/host/pci.zig`, `zigux/tests/phase12_nvme_pci.zig`, `Documentation/zigux/phase12-nvme-pci-slice.md`, shared `zigux/tests/phase12_build.zig` wiring, and the tranche-level `phase12` make target in `zigux/Makefile`.
- the broader Phase 12 tranche is now further along than this survey's earlier checkpoint: `drivers/net/virtio_net.zig` and `drivers/scsi/virtio_scsi.zig` are both landed bounded starters, so NVMe PCI should now be compared against peer driver starters rather than only against survey scaffolding.
- the landed starter stays intentionally narrow: it validates queue geometry, computes combined queue bytes and rounded DMA page demand, assigns monotonic admin and I/O queue identifiers, derives doorbell offsets, freezes queue planning across reset generations, records a bounded PRP buffer shape through first-page offset, rounded span, tail-page count, and PRP list bound checks, and now also records a bounded PRP metadata helper through command-inline data pointers, PRP-list-covered pages, extra descriptor DMA footprint, total DMA bytes, and reset-time descriptor rebuild need before any live DMA-backed queue work.
- the shared Phase 12 packet now also keeps the focused smoke preflight explicit: `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all` and `make -C zigux phase12-smoke` rerun the direct `nvme pci` starter ahead of the broader survey-backed replay, so this survey note should not leave that narrower driver-facing shard implied only by `zigux/tests/phase12_build.zig`, the Makefile, or the raw GitHub fallback map.
- that footing is useful, but it still does not cover PRP or SGL descriptor construction, Host Memory Buffer policy, blk-mq request submission, live PCI queue creation, IRQ routing, MMIO access, or recovery parity.
- the next honest driver-facing step is no longer another queue-planner helper inside this packet; the lane should stay parked until an explicitly approved transport-facing follow-up is ready beyond the now-landed PRP buffer-shape and PRP metadata helpers.

## Recorded gaps

The survey manifest now records:

- the landed `phase12-build-gate`
- the landed `phase12-make-target`
- the landed `phase12-nvme-pci-driver-starter`
- the landed `phase12-nvme-pci-driver-tests`
- the landed `phase12-nvme-pci-slice-note`
- the landed `phase12-virtio-net-driver-starter`
- the landed `phase12-virtio-scsi-driver-starter`
- the landed `phase12-nvme-pci-survey-gate`
- the landed `phase12-nvme-pci-survey-note`
- the landed `phase12-nvme-pci-prp-shape-helper`
- the landed `phase12-nvme-pci-prp-metadata-helper`
- the still-blocked `phase12-nvme-pci-dma-safe-transport-gap`
- the still-blocked `phase12-nvme-pci-throughput-and-recovery-gap`

This keeps the lane concrete and reviewable without overstating progress: the queue-planner plus PRP-shape plus PRP-metadata starters are real, but the transport-heavy roadmap work is still intentionally blocked.

## Non-goals

This survey slice does not claim:

- live PRP or SGL mapping
- Host Memory Buffer management
- blk-mq `queue_rq()` handling
- live PCI queue creation or teardown
- MSI or MSI-X setup, IRQ routing, or completion polling
- timeout-triggered reset plumbing, suspend or resume, or hardware-backed recovery

## Gates

1. run the focused smoke preflight
- `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
- `make -C zigux phase12-smoke`
- these rerun the direct `nvme pci` starter ahead of the broader survey-backed replay route.

2. run the dedicated Phase 12 build
- `zig build test --build-file zigux/tests/phase12_build.zig --summary all`

3. run the convenience target
- `make -C zigux phase12`

## Next bounded step

Keep this Phase 12 nvme PCI lane parked unless the roadmap explicitly approves a transport-facing follow-up beyond the now-landed queue-planning, PRP buffer-shape, and PRP metadata helpers.

Until that driver-local reopen is approved, keep this survey aligned with the shared smoke-plus-build replay packet instead of letting the focused preflight shard drift back into build-file-only, Makefile-only, or fallback-map-only knowledge.
