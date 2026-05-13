# Phase 12 NVMe PCI Reopen Governance

This note is the driver-local owner map for the bounded NVMe PCI lane family on current `master`.

It keeps the active `P12-L05` starter-present survey lane, the later `P12-Y02` reopen lane, and the shared Phase 12 release packet from collapsing into one blurry reminder surface while a bounded starter plus verifier packet is present and the broader survey, slice, and replay packet remains incomplete on current `master`.

## Status
- `PHASE12_STATUS=active`
- `PHASE12_LANE_KEY=P12-L05`
- scope: one bounded same-driver survey, owner-map, DMA-note, or recovery-governance follow-through tied only to the Phase 12 NVMe PCI packet
- later reopen alias: `P12-Y02`
- shared release-packet companion: `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
- driver-local reminder companions:
  - `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
  - `Documentation/zigux/phase12-release-sequencing.md`
  - `zigux/tests/README.md`

## Current Master Reality
Current `master` ships the bounded starter `drivers/nvme/host/pci.zig` together with the bounded verifier shard `drivers/nvme/host/pci_verify.zig`. Treat those files as queue-planning, PRP-shape, and reset-governance evidence only, not as proof that the broader direct survey and replay packet is already complete.

Treat each of these paths as still absent until a bounded reland publishes them again:

- `Documentation/zigux/phase12-nvme-pci-slice.md`
- `Documentation/zigux/phase12-nvme-pci-survey.md`
- `zigux/tests/phase12_nvme_pci.zig`
- `zigux/tests/phase12_nvme_pci_survey.zig`
- `zigux/tests/phase12_nvme_pci_manifest.json`

Because the starter is present again, `P12-L05` now owns the same-driver survey truthfulness and bounded queue-planning or recovery follow-through on current `master`. `P12-Y02` should stay framed as a later reopen alias for the broader packet or one owner-map cleanup once those still-missing slice, survey, and replay surfaces move.

## Ownership Split
- `P12-L05` owns the shipped direct starter packet: queue planning, queue-count reservation, PRP buffer-shape accounting, PRP metadata accounting, reset-summary bookkeeping, and bounded DMA-note or recovery-governance preflights that stay within the current starter-plus-verifier surface
- `P12-Y02` owns only a later same-driver reopen once the still-missing slice, survey, and replay packet exists again, or a driver-local owner-map cleanup that cannot be handled inside the active starter-present `P12-L05` survey pass
- the shared Phase 12 release packet remains outside this lane except for pointer updates that keep the starter-plus-verifier-versus-missing-replays split truthful
- `virtio_net`, `virtio_scsi`, and libbpf heavy-consumer reviewability are not part of this lane

## Allowed Follow-Through Shapes
A same-lane NVMe PCI follow-up may land exactly one of these shapes at a time:
1. a bounded survey or owner-map truthfulness repair that keeps the starter-plus-verifier surface explicit while the slice, survey, and replay packet stays absent on current `master`
2. a bounded DMA-note preflight sharpening what the starter can or cannot promise about host-side descriptor pressure without constructing live PRP or SGL mappings
3. a bounded recovery-governance preflight clarifying what reset-time bookkeeping must be true before a cached queue or descriptor plan can be counted as replay-ready

## Non-Goals
This lane does not claim:
- live DMA mapping, PRP or SGL list construction, or descriptor submission
- blk-mq request submission, tagset wiring, or hardware-backed queue creation
- MSI or MSI-X routing, interrupt completion flow, timeout plumbing, suspend or resume, or transport-backed reset recovery
- shared Phase 12 release closure beyond keeping the driver-local owner map truthful

## Review Rule
If a proposed NVMe PCI change touches files outside the driver-local reminder packet, owner-map note, starter shard, verifier shard, direct tests, or manifest, it should be treated as out of lane unless the only extra edit is a shared pointer update in `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`.

## Next Bounded Step
If the NVMe PCI lane family reopens again, keep it to one approved same-driver packet:
- leave `drivers/nvme/host/pci.zig` plus `drivers/nvme/host/pci_verify.zig` framed as the bounded starter-plus-verifier packet until the broader slice, survey, and replay surfaces actually land
- pair those shipped shards with the missing slice, survey, smoke replay, survey replay, and manifest packet before claiming a fully wired direct NVMe replay
- otherwise keep the follow-through to one driver-local truthfulness, DMA-note, or recovery-governance repair only

Do not widen into shared Phase 12 reminder churn or transport-heavy implementation claims.
