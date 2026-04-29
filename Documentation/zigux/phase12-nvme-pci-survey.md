# Phase 12 NVMe PCI Survey

This survey note records the current bounded Phase 12 checkpoint around `drivers/nvme/host/pci.c`.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_LANE_KEY=P12-L08`
- `PHASE12_SLICE=nvme-pci-survey`
- `PHASE12_SURVEYED_COMMIT=a8daee106057a542aa03f2983662bec7c06584bb`
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
- the broader Phase 12 tranche has now been re-verified at current `master` snapshot `a8daee106057a542aa03f2983662bec7c06584bb`, where the same three bounded complex-driver starters are still the truthful footing: `drivers/net/virtio_net.zig`, `drivers/scsi/virtio_scsi.zig`, and `drivers/nvme/host/pci.zig`, so NVMe PCI should keep being compared against peer driver starters rather than against survey scaffolding or unrelated lane churn.
- that refreshed head did not widen the NVMe PCI starter beyond the earlier queue-planner, PRP buffer-shape, and pointer-selection packet, which means the survey's roadmap gap remains transport- and recovery-heavy rather than merely stale.
- the landed starter stays intentionally narrow: it validates queue geometry, computes combined queue bytes and rounded DMA page demand, assigns monotonic admin and I/O queue identifiers, derives doorbell offsets, freezes queue planning across reset generations, records one tiny PRP buffer-shape summary with first-page offset, rounded span, and page-list bound checks, and now also records one tiny PRP-versus-SGL selection summary around page-gap forcing, user-command forcing, integrity-segment forcing, admin-queue limitations, and average-segment threshold preference before any live DMA-backed queue work.
- that footing is useful, but it still does not cover PRP or SGL descriptor allocation, Host Memory Buffer policy, blk-mq request submission, live PCI queue creation, IRQ routing, MMIO access, or recovery parity.
- the next honest driver-facing step is to keep this lane on survey or validation work until the roadmap-approved DMA-safe transport substrate exists for a truthful follow-up beyond the queue planner, PRP buffer-shape helper, and pointer-selection helper.

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
- the landed `phase12-nvme-pci-pointer-selection-helper`
- the still-blocked `phase12-nvme-pci-live-queue-and-dma`

This keeps the lane concrete and reviewable without overstating progress: the queue-planner plus PRP-shape plus pointer-selection starters are real, but the transport-heavy roadmap work is still intentionally blocked.

## Rollback And Reversible Delivery

- owner: `Storage Driver Lane`
- rollback owner: `Storage Driver Lane`
- fallback path: keep `drivers/nvme/host/pci.c` as the source of truth, keep the bounded `drivers/nvme/host/pci.zig` queue-planner, PRP-shape, and pointer-selection helpers on their current starter footing, and drop the Phase 12 nvme PCI survey packet out of `zigux/tests/phase12_build.zig` if the shared reviewability surface regresses.
- reversible delivery evidence: this Phase 12 packet stays additive around the bounded `drivers/nvme/host/pci.zig` starter, `zigux/tests/phase12_nvme_pci.zig`, `zigux/tests/phase12_nvme_pci_survey.zig`, and this survey note, so the survey gate can be removed without mutating `drivers/nvme/host/pci.c` or claiming live PCI queue, DMA, or reset parity.
- rollback drill: run `make -C zigux phase12-validate`; if the nvme PCI survey packet is the only failing slice, repair this note or `scripts/zigux/validate-phase12.py` first, otherwise remove the `phase12-nvme-pci-survey-tests` entry from `zigux/tests/phase12_build.zig`, keep the bounded driver starter and direct test intact, then rerun `make -C zigux phase12-validate` followed by `zig build test --build-file zigux/tests/phase12_build.zig --summary all`.

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
- `zig test zigux/tests/phase12_nvme_pci_survey.zig`
- `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
- current `master` snapshot `a8daee106057a542aa03f2983662bec7c06584bb` passed the shared Phase 12 replay with `Build Summary: 17/17 steps succeeded; 50/50 tests passed`, including `phase12-nvme-pci-tests 9 pass (9 total)` and `phase12-nvme-pci-survey-tests 1 pass (1 total)`.

## Next bounded step

Stay in the Phase 12 nvme PCI lane on survey or validation work until the roadmap-approved DMA-safe transport substrate exists for a truthful follow-up beyond the current queue planner, PRP buffer-shape helper, and pointer-selection helper.
