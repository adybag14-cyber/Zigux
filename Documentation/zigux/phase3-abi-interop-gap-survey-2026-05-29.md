# Phase 3 ABI Interop Gap Survey - 2026-05-29

This survey is a lane-local readback for `P3-L01`. It compares the Phase 3 roadmap target against current `master` without taking ownership of direct `zigux/bindings/abi.zig` repair work or widening into later runtime-core delivery.

## Grounding

Roadmap Phase 3 still defines the permanent C/Zigux boundary around:

- explicit export shims
- generated or curated bindings
- layout assertions
- explicit panic and allocator policy
- approved atomic, barrier, and MMIO wrappers
- narrow unsafe surfaces

The bootstrap ledger anchors the shared ABI packet at entry `26`, then records bounded follow-through slices for bitmap/cpumask, list/hlist, err_ptr/xarray, xarray slot, IDR slot, and the early IDA helper family.

## Current Repo Reality

Current `master` now shows a broader bounded interop surface than the older shared ABI survey refresh alone describes:

- the shared ABI substrate remains present through `include/zigux/abi.h`, `zigux/bindings/abi.zig`, `zigux/bindings/notifier_abi.zig`, `zigux/helpers/layout_assert.zig`, `zigux/kernel/export_shim.zig`, `zigux/unsafe/narrow.zig`, `zigux/tests/phase3_abi.zig`, and the shared Phase 3 validator routes
- the starter header-family and export/UAPI packet remains present through `include/linux/zigux.h`, `include/zigux/dev_t.h`, `zigux/uapi/dev_t.zig`, `zigux/uapi/version.zig`, `zigux/bindings/dev_t.zig`, `zigux/bindings/version.zig`, `zigux/bindings/header_family.zig`, and the focused export/UAPI replay tests
- bounded helper-local interop packets are live for bitmap/cpumask, list/hlist, err_ptr/xarray, xarray-slot, idr-slot, ida-bitmap, ida-alloc, and ida-range surfaces
- `zigux/tests/fixtures/phase3_abi_manifest.json` already lists the shared ABI packet, the current validation routes, and the returned `idr_slot` replay routes
- the helper-local IDA manifests for bitmap, allocation, and range each report no local `repo_reality_gaps` while staying intentionally outside broader IDA policy or runtime ownership

## Current Interop Gap

The remaining Phase 3 gap is no longer a missing skeleton. The real gap is integration maturity:

- the live repo has multiple bounded manifest-backed helper packets, but they remain helper-local survey and replay slices rather than a completed permanent C/Zigux ABI boundary
- direct large-file binding cleanup, including the known fused chrdev notify-ack tail in `zigux/bindings/abi.zig`, remains owned by the neighboring direct-binding repair lane and is not part of this survey lane
- IDA coverage currently reaches bitmap, allocation, and range helper-local packets, while range-set and policy follow-through are not visible as landed slice docs on current `master`
- the shared `phase3-abi-slice.md` survey refresh should be reread before any future edit because its current high-level status text undercounts the later IDR and IDA repo evidence even though the individual slice docs and manifests exist

## Next Safe Step

Keep `P3-L01` survey-local. The next useful same-lane repair is to align the shared ABI survey or a dedicated checker with the current IDR and IDA packet reality after a fresh readback of current `master`. Do not use this lane for direct `abi.zig` rewriting, wrapper proliferation, or broader Phase 3 completion claims.
