# Phase 12 NVMe PCI Survey

This survey note records the current bounded Phase 12 checkpoint around `drivers/nvme/host/pci.c`.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_LANE_KEY=P12-L08`
- `PHASE12_SLICE=nvme-pci-survey`
- `PHASE12_SURVEYED_COMMIT=8e6785d9e39f5b59531dabc7799b1caf72885850`
- scope: archival survey manifest, dedicated survey gate, shared Phase 12 build and make-target wiring, and a lane note that compares the landed `pci.zig` starter against the remaining roadmap gap and the current Phase 12 tranche state
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

That starter is real progress, but it is still only a narrow queue-and-data-pointer planning slice. The Linux anchor is 4,293 lines and mixes quirk parsing, admin-queue bring-up, MSI and MSI-X planning, blk-mq queue mapping, PRP and SGL setup, Host Memory Buffer controls, timeout and reset policy, PCI queue creation, completion polling, and suspend or teardown flows.

This survey keeps that difference explicit so the lane does not overclaim production-driver progress.

## Survey findings

- `drivers/nvme/host/pci.c` is present on `master` and remains a high-risk complex-driver anchor whose live behavior stretches far beyond the current Zigux starter.
- the live repo now ships `drivers/nvme/host/pci.zig`, `zigux/tests/phase12_nvme_pci.zig`, `Documentation/zigux/phase12-nvme-pci-slice.md`, shared `zigux/tests/phase12_build.zig` wiring, and the tranche-level `phase12` make target in `zigux/Makefile`.
- the broader Phase 12 tranche has now been re-verified at current `master` snapshot `8e6785d9e39f5b59531dabc7799b1caf72885850`, where the same three bounded complex-driver starters are still the truthful footing: `drivers/net/virtio_net.zig`, `drivers/scsi/virtio_scsi.zig`, and `drivers/nvme/host/pci.zig`, so NVMe PCI should keep being compared against peer driver starters rather than against survey scaffolding or unrelated lane churn.
- that refreshed head still left one truthful same-lane opening smaller than transport work: the live packet had queue-planner, PRP buffer-shape, and pointer-selection coverage, but it still lacked a bounded PRP metadata summary around descriptor footprint and reset-time rebuild pressure.
- the landed starter stays intentionally narrow: it validates queue geometry, computes combined queue bytes and rounded DMA page demand, assigns monotonic admin and I/O queue identifiers, derives doorbell offsets, freezes queue planning across reset generations, records one tiny PRP buffer-shape summary with first-page offset, rounded span, and page-list bound checks, now records one tiny PRP metadata summary with command-inline pointer count, PRP-list-covered pages, extra descriptor DMA footprint, and reset-time descriptor rebuild need, and also records one tiny PRP-versus-SGL selection summary around page-gap forcing, user-command forcing, integrity-segment forcing, admin-queue limitations, and average-segment threshold preference before any live DMA-backed queue work.
- that footing is useful, but it still does not cover PRP or SGL descriptor allocation, Host Memory Buffer policy, blk-mq request submission, live PCI queue creation, IRQ routing, MMIO access, or recovery parity.
- the next honest driver-facing step is one equally narrow recovery-facing helper or review note that keeps PRP metadata and reset-rebuild behavior explicit without widening into live DMA-backed transport work before the roadmap-approved DMA-safe substrate exists.

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
- the landed `phase12-nvme-pci-pointer-selection-helper`
- the still-blocked `phase12-nvme-pci-live-queue-and-dma`

This keeps the lane concrete and reviewable without overstating progress: the queue-planner plus PRP-shape plus PRP-metadata plus pointer-selection starters are real, but the transport-heavy roadmap work is still intentionally blocked.

## Non-goals

This survey slice does not claim:

- live PRP or SGL mapping
- PRP or SGL descriptor allocation
- Host Memory Buffer management
- blk-mq `queue_rq()` handling
- live PCI queue creation or teardown
- MSI or MSI-X setup, IRQ routing, or completion polling
- timeout-triggered reset plumbing, suspend or resume, or hardware-backed recovery

## Gates

1. run the dedicated Phase 12 build
- `zig build test --build-file zigux/tests/phase12_build.zig`

2. run the convenience target
- `make -C zigux phase12`

## Latest verification snapshot

- `zig fmt --check drivers/nvme/host/pci.zig zigux/tests/phase12_nvme_pci.zig zigux/tests/phase12_nvme_pci_survey.zig`
- `zig test drivers/nvme/host/pci.zig`
- `zig test --dep nvme_pci -Mroot=zigux/tests/phase12_nvme_pci.zig -Mnvme_pci=drivers/nvme/host/pci.zig`
- `zig test zigux/tests/phase12_nvme_pci_survey.zig`
- current `master` snapshot `8e6785d9e39f5b59531dabc7799b1caf72885850` passed the focused NVMe PCI replay with `All 0 tests passed.` for `drivers/nvme/host/pci.zig`, `All 11 tests passed.` for `zigux/tests/phase12_nvme_pci.zig`, and `All 1 tests passed.` for `zigux/tests/phase12_nvme_pci_survey.zig`.

## Next bounded step

Stay in the Phase 12 nvme PCI lane on one equally narrow recovery-facing helper or reviewability step that builds on the current queue planner, PRP buffer-shape helper, PRP metadata helper, and pointer-selection helper without widening into live DMA-backed transport work.
