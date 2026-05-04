# Phase 12 NVMe PCI Raw GitHub Fallback Map

This note records the smallest public-read fallback packet for lane `P12-L08`.

It does not claim a live-head replay catalog. It only maps the archived Phase 12 NVMe PCI survey packet to stable GitHub tree views and raw blob URLs pinned to `8b69e4dfd04553afeb08c0ecbf3060f800e7ecd1`.

The dedicated `zigux/tests/phase12_nvme_pci_survey.zig` gate reads this note back as part of the archived reviewability surface, so fallback coverage stays inside the NVMe packet instead of drifting into cross-lane memory.

## Scope

- `PHASE12_LANE_KEY=P12-L08`
- `PHASE12_SURVEYED_COMMIT=8b69e4dfd04553afeb08c0ecbf3060f800e7ecd1`
- bounded packet:
  - `drivers/nvme/host/pci.c`
  - `drivers/nvme/host/pci.zig`
  - `zigux/tests/phase12_nvme_pci.zig`
  - `zigux/tests/phase12_nvme_pci_manifest.json`
  - `zigux/tests/phase12_nvme_pci_survey.zig`
  - `zigux/tests/phase12_build.zig`
  - `Documentation/zigux/phase12-nvme-pci-slice.md`
  - `Documentation/zigux/phase12-nvme-pci-survey.md`
  - `scripts/zigux/validate-phase12.py`
  - `zigux/Makefile`

## Tree Readback Roots

- `https://github.com/adybag14-cyber/Zigux/tree/master/drivers/nvme/host`
- `https://github.com/adybag14-cyber/Zigux/tree/master/Documentation/zigux`
- `https://github.com/adybag14-cyber/Zigux/tree/master/zigux/tests`

## Raw Pinned URLs

- `https://raw.githubusercontent.com/adybag14-cyber/Zigux/8b69e4dfd04553afeb08c0ecbf3060f800e7ecd1/drivers/nvme/host/pci.c`
- `https://raw.githubusercontent.com/adybag14-cyber/Zigux/8b69e4dfd04553afeb08c0ecbf3060f800e7ecd1/drivers/nvme/host/pci.zig`
- `https://raw.githubusercontent.com/adybag14-cyber/Zigux/8b69e4dfd04553afeb08c0ecbf3060f800e7ecd1/zigux/tests/phase12_nvme_pci.zig`
- `https://raw.githubusercontent.com/adybag14-cyber/Zigux/8b69e4dfd04553afeb08c0ecbf3060f800e7ecd1/zigux/tests/phase12_nvme_pci_manifest.json`
- `https://raw.githubusercontent.com/adybag14-cyber/Zigux/8b69e4dfd04553afeb08c0ecbf3060f800e7ecd1/zigux/tests/phase12_nvme_pci_survey.zig`
- `https://raw.githubusercontent.com/adybag14-cyber/Zigux/8b69e4dfd04553afeb08c0ecbf3060f800e7ecd1/zigux/tests/phase12_build.zig`
- `https://raw.githubusercontent.com/adybag14-cyber/Zigux/8b69e4dfd04553afeb08c0ecbf3060f800e7ecd1/Documentation/zigux/phase12-nvme-pci-slice.md`
- `https://raw.githubusercontent.com/adybag14-cyber/Zigux/8b69e4dfd04553afeb08c0ecbf3060f800e7ecd1/Documentation/zigux/phase12-nvme-pci-survey.md`
- `https://raw.githubusercontent.com/adybag14-cyber/Zigux/8b69e4dfd04553afeb08c0ecbf3060f800e7ecd1/scripts/zigux/validate-phase12.py`
- `https://raw.githubusercontent.com/adybag14-cyber/Zigux/8b69e4dfd04553afeb08c0ecbf3060f800e7ecd1/zigux/Makefile`

## Use

- Start with the tree readback roots when the connector can still show the current repo structure but a lane reviewer needs a public fallback path.
- Use the raw pinned URLs when the exact archived Phase 12 NVMe PCI packet text matters more than the moving `master` tip.
- Leave current-head replay evidence to the owner lanes for the shared validator, the shared build, or a dedicated driver-local current-replay catalog.

## Ownership And Rollback

- owner: `NVMe PCI Lane`
- rollback owner: `NVMe PCI Lane`
- fallback path: keep `drivers/nvme/host/pci.c` as the source of truth, keep the bounded `drivers/nvme/host/pci.zig` queue planner plus queue-count, doorbell-window, queue-recovery replay, PRP buffer-shape, PRP metadata helper, and pointer-selection helpers reviewable in isolation, and leave shared-build entrypoint changes to the shared Phase 12 packet rather than this archival fallback map.

## Latest Live Recheck

- rechecked public host-path history on `master` through the GitHub connector rather than a local clone, because direct public clone and raw-fetch paths remain blocked in this runtime.
- the archived fallback packet is still pinned to `8b69e4dfd04553afeb08c0ecbf3060f800e7ecd1`; it should not be read as the current `master` tip.
- same-family live deltas after that archived packet now include `feat(zigux): add bounded nvme pci doorbell window helper` (`8809723`), `feat(zigux): add nvme pci queue count planning helper` (`7459e961262eeec728952226725685fd543f3644`), and `fix(nvme): count inline prp pointers for list metadata` (`f718b088df0b025c4ec1a9598be4d97c3c702bdf`).
- the current live starter now also carries a bounded queue-recovery replay helper that keeps capped I/O queue replay, preserved admin geometry, aggregate host DMA demand, and reset-frozen visibility reviewable without claiming live queue recreation, MMIO, IRQ routing, blk-mq submission, or recovery parity.
- a future current-head replay for this lane should therefore include the queue-count helper, the repaired inline-pointer-count semantics, and the queue-recovery replay helper instead of treating them as separate transport expansion.

## Non-goals

- no `current_master_replay_head`
- no shared-validator outcome snapshot
- no shared-build outcome snapshot
- no claim that `8b69e4dfd04553afeb08c0ecbf3060f800e7ecd1` is the current `master` tip
