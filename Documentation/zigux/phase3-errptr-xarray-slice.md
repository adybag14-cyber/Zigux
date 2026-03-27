# Phase 3 ErrPtr/XArray Value Interop Slice

This document defines the fourth bounded Phase 3 slice for Zigux.

## Status

- `PHASE3_STATUS=active`
- `PHASE3_SLICE=errptr-xarray-value-interop`
- scope: curated `ERR_PTR` and encoded value-entry helpers only
- product boundary:
  - `include/zigux/abi.h`
  - `include/linux/zigux.h`
  - `zigux/helpers/err_ptr.zig`
  - `zigux/helpers/xa_value.zig`
  - `zigux/tests/phase3_errptr_xarray_dump.zig`

## Why this slice exists

After bitmap/cpumask and list/hlist, the next useful Linux-facing boundary seam is encoded pointer state.

The correct bounded step is:

- stable `ERR_PTR` encoding and decoding helpers
- stable encoded value-entry helpers for future xarray-like work
- stable summary structs for both cases
- one committed C-vs-Zig parity fixture

This gives Zigux a clean way to model common Linux boundary sentinels without pretending to port full xarray, IDR, or pointer-tagging subsystems.

## Gates

1. validate Phase 3 slice shape
- `python3 scripts/zigux/validate-phase3.py`

2. check C-vs-Zig err_ptr/xarray parity
- `python3 scripts/zigux/check-phase3-errptr-xarray.py`

3. run the wider Phase 3 substrate tests
- `zig build phase3-test --build-file zigux/tests/build.zig`

- `PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py`
- `PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-errptr-xarray.py`
- `PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig`

## Interop rules

- `ERR_PTR` helpers operate on raw address values, not ownership wrappers.
- encoded value-entry helpers stay bounded to the plain value-entry encoding only.
- this slice does not model internal xarray entries, retries, or node topology.
- allocator behavior is not introduced here.

## Boundary

This slice does not claim:

- full `include/linux/err.h` replacement
- full `include/linux/xarray.h` replacement
- IDA or IDR allocation
- tagged internal entry semantics beyond plain value-entry encoding
- runtime xarray storage or traversal

This slice only closes the first permanent err_ptr and encoded value-entry interop seam on top of the existing Phase 3 ABI substrate.