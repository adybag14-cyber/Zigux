# Phase 12 NVMe PCI Reopen Governance

This note is the driver-local owner map for the bounded NVMe PCI lane family on current `master`.

It keeps the historical `P12-L05` starter lane, the later `P12-Y02` reopen lane, and the shared Phase 12 release packet from collapsing into one blurry reminder surface while only a bounded verifier shard is present and the broader direct NVMe PCI starter packet is absent on current `master`.

## Status
- `PHASE12_STATUS=active`
- `PHASE12_LANE_KEY=P12-Y02`
- scope: one bounded same-driver owner-map, verifier-shard truthfulness, DMA-note, or recovery-governance follow-through tied only to the Phase 12 NVMe PCI packet
- historical starter owner: `P12-L05`
- shared release-packet companion: `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
- driver-local reminder companions:
  - `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
  - `Documentation/zigux/phase12-release-sequencing.md`
  - `zigux/tests/README.md`

## Current Master Reality
Current `master` does not materialize the direct NVMe PCI starter packet, but it does ship the bounded verifier shard `drivers/nvme/host/pci_verify.zig`. Treat that verifier shard as queue-planning and reset-governance evidence only, not as proof that the broader direct starter packet has already returned.

Treat each of these paths as absent until a bounded reland publishes them again:

- `drivers/nvme/host/pci.zig`
- `Documentation/zigux/phase12-nvme-pci-slice.md`
- `Documentation/zigux/phase12-nvme-pci-survey.md`
- `zigux/tests/phase12_nvme_pci.zig`
- `zigux/tests/phase12_nvme_pci_survey.zig`
- `zigux/tests/phase12_nvme_pci_manifest.json`

Because that broader starter packet is absent, `P12-Y02` must not speak as if it is reopening an already-shipped direct driver file on current `master`. The first honest direct-driver follow-up remains a bounded `P12-L05` reland of the missing starter packet itself, while the existing verifier shard can anchor same-lane owner-map truthfulness and bounded queue-planning or reset-bookkeeping reminders without implying direct driver closure.

## Ownership Split
- `P12-L05` owns the direct NVMe PCI starter packet: queue planning, queue-count reservation, queue-reservation replay, PRP buffer-shape accounting, PRP metadata accounting, recovery replay bookkeeping, and the bounded dropped-I/O retirement helper once those files are actually materialized again on current `master`
- `P12-Y02` owns only a same-driver reopen after the direct starter packet exists again, or a driver-local owner-map or verifier-shard truthfulness repair while it does not
- the shared Phase 12 release packet remains outside this lane except for pointer updates that keep the verifier-present-versus-direct-starter-absent split truthful
- `virtio_net`, `virtio_scsi`, and libbpf heavy-consumer reviewability are not part of this lane

## Allowed Reopen Shapes
A `P12-Y02` follow-up may land exactly one of these shapes at a time:
1. a bounded owner-map or verifier-shard truthfulness repair that keeps the existing verifier-only surface explicit while the direct NVMe PCI starter packet stays absent on current `master`
2. a bounded DMA-note preflight after the `P12-L05` starter packet is materialized again, sharpening what the starter can or cannot promise about host-side descriptor pressure without constructing live PRP or SGL mappings
3. a bounded recovery-governance preflight after the `P12-L05` starter packet is materialized again, clarifying what reset-time bookkeeping must be true before a cached queue or descriptor plan can be counted as replay-ready

## Non-Goals
This lane does not claim:
- live DMA mapping, PRP or SGL list construction, or descriptor submission
- blk-mq request submission, tagset wiring, or hardware-backed queue creation
- MSI or MSI-X routing, interrupt completion flow, timeout plumbing, suspend or resume, or transport-backed reset recovery
- shared Phase 12 release closure beyond keeping the driver-local owner map truthful

## Review Rule
If a proposed `P12-Y02` change touches files outside the NVMe PCI reminder packet, owner-map note, verifier shard, direct driver packet, direct tests, or manifest, it should be treated as out of lane unless the only extra edit is a shared pointer update in `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`.

## Next Bounded Step
If the NVMe PCI lane family reopens again, keep it to one approved same-driver packet:
- leave `drivers/nvme/host/pci_verify.zig` framed as the bounded verifier-only shard until the broader starter reland actually lands
- reland the missing `P12-L05` starter surfaces first if the work needs a direct driver file
- otherwise keep the follow-through to one driver-local truthfulness, verifier-shard, or owner-map repair only

Do not widen into shared Phase 12 reminder churn or transport-heavy implementation claims.
