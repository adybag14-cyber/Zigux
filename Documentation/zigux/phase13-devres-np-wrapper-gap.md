# Phase 13 devres NP Wrapper Gap

## Status
- `PHASE13_STATUS=active`
- `PHASE13_LANE=P13-L06`
- `PHASE13_SCOPE=iomap-mmio-safety-np-wrapper-gap`
- `PHASE13_READBACK=master-readback-2026-05-16`

## Packet Reading
- The Phase 13 roadmap still keeps `lib/devres.c` inside bounded shared-helper delivery, so the live `lib/devres.zig` packet remains helper-first rather than a claim of live MMIO, DMA, scatterlist, device-tree, or arch-memtype parity.
- Current helper and replay evidence already expose the non-posted wrapper path directly: `lib/devres.zig` carries `planManagedIoremapAcquireNp(` and `zigux/tests/phase13_devres.zig` keeps the direct replay `phase13 devres non-posted ioremap wrapper forces the NP lifetime path`.
- `Documentation/zigux/phase13-devres-slice.md` already records the same behavior one level up by saying the managed-resource planner switches plain requests to the non-posted variant when resource flags demand it.
- The remaining drift is reviewability-local rather than helper-local: `scripts/zigux/check-phase13-devres-packet-alignment.py` still pins the slice summary through `devm_ioremap_uc()` and `devm_ioremap_wc()` without an explicit `devm_ioremap_np()` marker, so the manifest-backed wrapper summary can lag behind the shipped helper and direct replay.
- This note exists only because the run landed a substantive validation follow-through in `scripts/zigux/check-phase13-devres-np-wrapper-gap.py`; it is not a claim that the broader devres survey, release packet, or DMA/scatterlist packet changed ownership.

## Next Bounded Step
Refresh `zigux/tests/phase13_devres_manifest.json`, `zigux/tests/phase13_devres_reviewability.zig`, and `scripts/zigux/check-phase13-devres-packet-alignment.py` together when a safe full-file write path is available, so the manifest-backed wrapper summary names the same non-posted wrapper surface that the helper, direct replay, and slice note already expose.
