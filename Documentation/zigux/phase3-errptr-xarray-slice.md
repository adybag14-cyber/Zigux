# Phase 3 err_ptr/xarray Slice

This note records one bounded Phase 3 helper-side interop slice on current `master`.

## Current Slice

- `zigux/helpers/err_ptr.zig`
- `zigux/helpers/xa_value.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`
- `scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`

## Bounded Contract

The helper pair stays intentionally small:

- `zigux/helpers/err_ptr.zig` only models the Linux `MAX_ERRNO` tag band as a pointer-sized integer encoding
- `zigux/helpers/xa_value.zig` only models the low-bit inline-value tag and rejects values that would enter the `err_ptr` band
- `zigux/tests/phase3_errptr_xarray_starter_packet.zig` proves that accepted inline values round-trip cleanly and that overlapping encodings fail closed

## Current Gap

This is not the broader Phase 3 ABI, export/UAPI, catalog, or low-level-wrapper packet that older reminder surfaces still name. It is one helper-local interop proof layered beside the existing `dev_t` starter packet.

Current shared reminder follow-up still belongs to the broader Phase 3 truthfulness pass:

- `Documentation/zigux/README.md`
- `zigux/tests/README.md`
- `Documentation/zigux/review-checklist.md`

Those surfaces still talk in broader Phase 3 packet terms and should be narrowed separately instead of being treated as proof that the wider validator or export-boundary routes already ship on `master`.

## Scope

This note is limited to the helper-local `err_ptr` and `xarray` value-tag boundary. It does not claim runtime pointer dereference behavior, export-shim wiring, broader UAPI layout support, IDR or IDA coverage, or any shared `phase3` replay route.
