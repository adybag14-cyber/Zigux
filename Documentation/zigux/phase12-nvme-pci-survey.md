# Phase 12 NVMe PCI Survey

This survey note records the current bounded Phase 12 checkpoint around `drivers/nvme/host/pci.c`.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_LANE_KEY=P12-L07`
- `PHASE12_SLICE=nvme-pci-survey`
- `PHASE12_SURVEYED_COMMIT=8b69e4dfd04553afeb08c0ecbf3060f800e7ecd1`
- scope: archival survey manifest, dedicated survey gate, shared Phase 12 build and make-target wiring, and a lane note that compares the landed `pci.zig` starter against the remaining roadmap gap and the current Phase 12 tranche state
- product boundary:
  - `drivers/nvme/host/pci.zig`
  - `zigux/tests/phase12_nvme_pci.zig`
  - `zigux/tests/phase12_nvme_pci_manifest.json`
  - `zigux/tests/phase12_nvme_pci_survey.zig`
  - `zigux/tests/phase12_build.zig`
  - `Documentation/zigux/phase12-nvme-pci-slice.md`
  - `Documentation/zigux/phase12-nvme-pci-survey.md`
  - `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`

## Why this slice exists

The Phase 12 roadmap explicitly names `drivers/nvme/host/pci.c` as a complex production-driver target, and the live repo now has a bounded `drivers/nvme/host/pci.zig` starter.

That starter is real progress, but it is still only a narrow queue-and-data-pointer planning slice with one bounded doorbell-window summary and one bounded PRP metadata summary. The Linux anchor is 4,293 lines and mixes quirk parsing, admin-queue bring-up, MSI and MSI-X planning, blk-mq queue mapping, PRP and SGL setup, Host Memory Buffer controls, timeout and reset policy, PCI queue creation, completion polling, and suspend or teardown flows.

This survey keeps that difference explicit so the lane does not overclaim production-driver progress.

This lane now also carries a tiny public-read fallback map in `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` so the archived packet can be reviewed through pinned GitHub tree and raw URLs without borrowing the separate `virtio_scsi` current-replay catalog.

The dedicated survey gate now treats that pinned fallback map as part of this packet's reviewability surface, so public-read fallback coverage stays inside the NVMe lane instead of drifting back into cross-lane memory.

## Survey findings

- `drivers/nvme/host/pci.c` is present on `master` and remains a high-risk complex-driver anchor whose live behavior stretches far beyond the current Zigux starter.
- the live repo now ships `drivers/nvme/host/pci.zig`, `zigux/tests/phase12_nvme_pci.zig`, `Documentation/zigux/phase12-nvme-pci-slice.md`, shared `zigux/tests/phase12_build.zig` wiring, and the tranche-level `phase12` make target in `zigux/Makefile`.
- the broader Phase 12 tranche is still published from packet-local verification head `8b69e4dfd04553afeb08c0ecbf3060f800e7ecd1`, where the same three bounded complex-driver starters are the truthful footing: `drivers/net/virtio_net.zig`, `drivers/scsi/virtio_scsi.zig`, and `drivers/nvme/host/pci.zig`. That keeps NVMe PCI compared against peer driver starters rather than survey scaffolding or unrelated lane churn without claiming the pinned survey head is the current `master` tip.
- that pinned verification head captured the earlier queue-planner, PRP buffer-shape, PRP metadata, and pointer-selection packet, while the current live starter now also carries one bounded doorbell-window helper so the packet can summarize SQ and CQ register aperture planning without reopening live MMIO or IRQ routing work.
- the older cross-lane breakage previously carried forward in this note no longer matches the live file contents on current `master`: rereading `scripts/zigux/validate-phase12.py` and `zigux/tests/phase12_virtio_net_survey.zig` shows the exact stale `SyntaxError: '{' was never closed` and `expected ')', found 'EOF'` claims are not present in the current shared sources, so this survey should stop presenting that historical failure report as live Phase 12 truth without a fresh owner-lane replay.
- the landed starter stays intentionally narrow: it validates queue geometry, computes combined queue bytes and rounded DMA page demand, assigns monotonic admin and I/O queue identifiers, derives doorbell offsets, records one tiny doorbell-window summary with admin and I/O queue-pair aperture totals plus reset visibility, freezes queue planning across reset generations, records one tiny PRP buffer-shape summary with first-page offset, rounded span, and page-list bound checks, records one tiny PRP metadata summary with command-inline data-pointer count, PRP-list-covered pages, extra descriptor DMA footprint, and reset-time descriptor rebuild need, and also records one tiny PRP-versus-SGL selection summary around page-gap forcing, user-command forcing, integrity-segment forcing, admin-queue limitations, and average-segment threshold preference before any live DMA-backed queue work.
- that footing is useful, but it still does not cover PRP or SGL descriptor allocation, Host Memory Buffer policy, blk-mq request submission, live PCI queue creation, IRQ routing, MMIO access, or recovery parity.
- the next honest driver-facing step is to keep this lane on survey or validation work until the roadmap-approved DMA-safe transport substrate exists for a truthful follow-up beyond the queue planner, doorbell-window helper, PRP buffer-shape helper, PRP metadata helper, and pointer-selection helper.

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
- the landed `phase12-nvme-pci-doorbell-window-helper`
- the landed `phase12-nvme-pci-pointer-selection-helper`
- the still-blocked `phase12-nvme-pci-live-queue-and-dma`

Within that same recorded survey-note gap, the packet now treats `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` as reviewable evidence for the archived public-read path.

Within that same recorded starter packet, the current live code, tests, and slice note also keep the bounded PRP metadata helper and doorbell-window helper reviewable without claiming live descriptor allocation, live MMIO, or transport work.

This keeps the lane concrete and reviewable without overstating progress: the queue-planner plus doorbell-window plus PRP-shape plus PRP-metadata plus pointer-selection starters are real, but the transport-heavy roadmap work is still intentionally blocked.

## Rollback And Reversible Delivery

- owner: `Storage Driver Lane`
- rollback owner: `Storage Driver Lane`
- fallback path: keep `drivers/nvme/host/pci.c` as the source of truth, keep the bounded `drivers/nvme/host/pci.zig` queue planner plus doorbell-window, PRP buffer-shape, and pointer-selection helpers reviewable in isolation, and drop the direct `phase12-nvme-pci-tests` plus `phase12-nvme-pci-survey-tests` entries out of `zigux/tests/phase12_build.zig` if the shared packet regresses.
- reversible delivery evidence: this Phase 12 packet only adds one bounded `drivers/nvme/host/pci.zig` starter, its paired `zigux/tests/phase12_nvme_pci.zig` and `zigux/tests/phase12_nvme_pci_survey.zig` review gates, the slice note, this survey note, and the pinned raw-read fallback map around the existing C anchor, so the lane can be narrowed again without inventing live PRP or SGL mapping, Host Memory Buffer policy, blk-mq request submission, live MMIO, IRQ routing, or PCI queue lifecycle parity.
- rollback drill: run `make -C zigux phase12-validate`; if the nvme PCI packet is the only failing slice, repair `Documentation/zigux/phase12-nvme-pci-survey.md`, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, or `zigux/tests/phase12_nvme_pci_survey.zig` first when only the reviewability record drifted, otherwise remove the `phase12-nvme-pci-tests` and `phase12-nvme-pci-survey-tests` entries from `zigux/tests/phase12_build.zig`, keep `drivers/nvme/host/pci.c` plus the bounded Zig starter unchanged, then rerun `make -C zigux phase12-validate` followed by `zig build test --build-file zigux/tests/phase12_build.zig --summary all` so the shared Phase 12 tranche stays truthful while the survey packet is repaired.

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
- `python3 -m py_compile scripts/zigux/validate-phase12.py`
- `zig test zigux/tests/phase12_nvme_pci_survey.zig`
- `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
- the published focused NVMe verification snapshot is still pinned to packet-local head `8b69e4dfd04553afeb08c0ecbf3060f800e7ecd1`, where `phase12-nvme-pci-survey-tests` passed `1/1`; treat the command and result lines below as archived packet evidence rather than a claim about the current `master` tip.
- a fresh live reread of `scripts/zigux/validate-phase12.py` and `zigux/tests/phase12_virtio_net_survey.zig` shows the older shared-lane syntax and EOF failures recorded by this survey are stale historical evidence rather than current repo truth.
- the same archived packet now also carries `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, and the dedicated survey gate reads that note back as part of the archived reviewability surface.
- the current live starter now also carries the bounded `phase12-nvme-pci-doorbell-window-helper` surface, but this lane has not repinned the archived raw fallback map or current-master replay head around it.
- this NVMe lane did not rerun the shared Phase 12 validator or shared Zig replay in the current pass, so the next shared-tranche status update belongs to the owner of the validator or virtio_net survey packet rather than to this note.
- even on the archived packet-local replay, the shared bundle still reached `phase12-nvme-pci-tests 11 pass (11 total)` and `phase12-nvme-pci-survey-tests 1 pass (1 total)` before the unrelated cross-lane stop recorded at the time.

## Next bounded step

Stay in the Phase 12 nvme PCI lane on survey or validation work until the roadmap-approved DMA-safe transport substrate exists for a truthful follow-up beyond the current queue planner, doorbell-window helper, PRP buffer-shape helper, PRP metadata helper, and pointer-selection helper. If this note reopens before then, refresh only the exact replay evidence for this packet or the pinned raw-read fallback map, and leave shared-validator or shared-build status refreshes to their own Phase 12 lanes.
