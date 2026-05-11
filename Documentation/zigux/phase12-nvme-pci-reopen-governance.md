# Phase 12 NVMe PCI Reopen Governance

This note is the driver-local owner map for the bounded NVMe PCI reopen packet on current `master`.

It exists to keep the landed `drivers/nvme/host/pci.zig` starter reviewable without letting a same-driver reopen blur together the original starter lane, the shared Phase 12 release packet, and blocked transport-heavy follow-through.

## Status
- `PHASE12_STATUS=active`
- `PHASE12_LANE_KEY=P12-Y02`
- scope: one bounded same-driver DMA-note, recovery-governance, or ownership follow-through tied only to `drivers/nvme/host/pci.zig`
- historical starter owner: `P12-L05`
- shared release-packet companion: `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
- driver-local evidence companions:
  - `Documentation/zigux/phase12-nvme-pci-slice.md`
  - `Documentation/zigux/phase12-nvme-pci-survey.md`
  - `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
  - `drivers/nvme/host/pci.zig`
  - `drivers/nvme/host/pci_verify.zig`

## Ownership Split
- `P12-L05` remains the owner of the already-landed starter surface: queue planning, queue-count reservation, queue-reservation replay, PRP buffer-shape accounting, PRP metadata accounting, recovery replay bookkeeping, and the bounded dropped-I/O retirement helper already described in the slice and survey notes.
- `P12-Y02` owns only a same-driver reopen that stays below live DMA mapping and closes one bounded gap in one run.
- The shared Phase 12 release packet remains outside this lane except for adding or refreshing a pointer back to this note when the owner map changes.
- `virtio_net`, `virtio_scsi`, and libbpf heavy-consumer reviewability are not part of this lane.

## Allowed Reopen Shapes
A `P12-Y02` follow-up may land exactly one of these shapes at a time:
1. a bounded DMA-note preflight that sharpens what the starter can or cannot promise about host-side descriptor pressure without constructing live PRP or SGL mappings
2. a bounded recovery-governance preflight that clarifies what reset-time bookkeeping must be true before a cached queue or descriptor plan can be counted as replay-ready
3. a bounded ownership repair that removes ambiguity between the historical starter lane, this reopen lane, and the shared Phase 12 packet

## Non-Goals
This lane does not claim:
- live DMA mapping, PRP or SGL list construction, or descriptor submission
- blk-mq request submission, tagset wiring, or hardware-backed queue creation
- MSI or MSI-X routing, interrupt completion flow, timeout plumbing, suspend or resume, or transport-backed reset recovery
- shared Phase 12 release closure beyond keeping the driver-local owner map truthful

## Review Rule
If a proposed `P12-Y02` change touches files outside the NVMe PCI slice, survey, fallback map, verifier, tests, or `drivers/nvme/host/pci.zig`, it should be treated as out of lane unless the only extra edit is a shared pointer update in `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`.

## Next Bounded Step
If this driver-local lane reopens again, keep it to one approved same-driver packet that either narrows descriptor-side DMA wording, narrows reset-time replay bookkeeping, or refreshes the owner map after a landed bounded helper. Do not widen into shared Phase 12 reminder churn or transport-heavy implementation claims.
