# Phase 3 Bitmap/Cpumask Interop Slice

This document defines the second bounded Phase 3 slice for Zigux.

## Status

- `PHASE3_STATUS=active`
- `PHASE3_SLICE=bitmap-cpumask-view-interop`
- scope: curated bitmap/cpumask boundary helpers only
- product boundary:
  - `include/zigux/abi.h`
  - `include/linux/zigux.h`
  - `zigux/helpers/bitmap_view.zig`
  - `zigux/helpers/cpumask_view.zig`
  - `zigux/tests/phase3_bitmap_cpumask_dump.zig`

## Why this slice exists

The ABI substrate by itself is not enough.
Phase 3 now needs the first real reusable interop helpers on top of that substrate.

The correct next step is still small:

- bitmap view constructors and validation
- first-set / first-zero / weight helpers
- cpumask view constructors and validation
- first / next / weight helpers
- stable summary structs
- one C-vs-Zig parity fixture

This keeps the slice reviewable while proving that Zigux can carry Linux-style bitmap and cpumask semantics through the permanent C/Zig boundary.

## Gates

1. validate Phase 3 slice shape
- `python3 scripts/zigux/validate-phase3.py`

2. check C-vs-Zig bitmap/cpumask parity
- `python3 scripts/zigux/check-phase3-bitmap-cpumask.py`

3. run the wider Phase 3 substrate tests
- `zig build phase3-test --build-file zigux/tests/build.zig`

- `PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py`
- `PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-bitmap-cpumask.py`
- `PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig`

## Interop rules

- `zigux_bitmap_view` stays an address-plus-shape descriptor, not an ownership container.
- `zigux_cpumask_view` stays a CPU-specific wrapper over the bitmap view model.
- new summary structs must remain plain layout-only ABI types.
- all raw address-to-slice conversion must stay inside `zigux/unsafe/narrow.zig`.
- no allocator behavior is introduced in this slice.

## Boundary

This slice does not claim:

- full `include/linux/bitmap.h` replacement
- full `include/linux/cpumask.h` replacement
- hotplug masks
- scheduler affinity policy
- generated bindings
- runtime scheduler integration

This slice only closes the first permanent bitmap/cpumask interop seam on top of the existing Phase 3 ABI substrate.
