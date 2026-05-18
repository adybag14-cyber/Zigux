# Phase 3 err_ptr/xarray Slice

This note records one bounded Phase 3 helper-side interop slice on current `master`.

## Current Slice

- `zigux/helpers/err_ptr.zig`
- `zigux/helpers/xa_value.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`
- `zigux/tests/phase3_errptr_xarray_dump.zig`
- `zigux/tests/phase3_errptr_xarray_dump_build.zig`
- `zigux/tests/fixtures/phase3_errptr_xarray/phase3_errptr_xarray_c_harness.c`
- `zigux/tests/fixtures/phase3_errptr_xarray/expected.json`
- `zigux/tests/fixtures/phase3_errptr_xarray_manifest.json`
- `scripts/zigux/check-phase3-errptr-xarray.py`

## Bounded Contract

The helper pair stays intentionally small:

- `zigux/helpers/err_ptr.zig` only models the Linux `MAX_ERRNO` tag band as a pointer-sized integer encoding
- `zigux/helpers/xa_value.zig` only models the low-bit inline-value tag and rejects values that would enter the `err_ptr` band
- `zigux/tests/phase3_errptr_xarray_starter_packet.zig` proves that accepted inline values round-trip cleanly, that the highest tagged inline boundary still stays below the `err_ptr` floor, and that overlapping encodings fail closed

## Current Replay Surface

The current helper-local packet now has three bounded replay layers:

- one manifest-backed starter packet:
  - `zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json`
  - `scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`
  - `python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py --self-test`
  - `python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`
- one fixture-backed parity packet:
  - `zigux/tests/phase3_errptr_xarray_dump.zig`
  - `zigux/tests/phase3_errptr_xarray_dump_build.zig`
  - `zigux/tests/fixtures/phase3_errptr_xarray/phase3_errptr_xarray_c_harness.c`
  - `zigux/tests/fixtures/phase3_errptr_xarray/expected.json`
  - `zigux/tests/fixtures/phase3_errptr_xarray_manifest.json`
  - `scripts/zigux/check-phase3-errptr-xarray.py`
  - `python3 scripts/zigux/check-phase3-errptr-xarray.py --self-test`
  - `python3 scripts/zigux/check-phase3-errptr-xarray.py --repo-root . --zig zig --cc gcc`
  - `zig build phase3-errptr-xarray-dump --build-file zigux/tests/phase3_errptr_xarray_dump_build.zig`
- two dedicated shared tests-root companions:
  - `zigux/tests/build.zig`
  - `zig build phase3-errptr-xarray-starter-packet --build-file zigux/tests/build.zig`
  - `zig build phase3-errptr-xarray-dump --build-file zigux/tests/build.zig`

That fixture-backed parity packet keeps one tiny C-vs-Zig comparison explicit, and the shared tests root now also exposes separate starter and dump step names for the slice without yet claiming a combined shared `phase3-errptr-xarray` route.

## Current Gap

This is still not the broader Phase 3 ABI, export/UAPI, catalog, or low-level-wrapper packet that older reminder surfaces still name. It is one helper-local interop proof layered beside the existing `dev_t` starter packet plus two dedicated shared step names in `zigux/tests/build.zig`.

Current same-area follow-through should stay limited to the remaining combined shared-route wiring and any later reminder-surface drift:

- `zigux/tests/build.zig`
- `Documentation/zigux/phase3-shared-reminder-gap.md`

That follow-through should stay separate instead of being treated as proof that the wider validator or export-boundary routes already ship on `master`.

## Scope

This note is limited to the helper-local `err_ptr` and `xarray` value-tag boundary, one tiny fixture-backed parity dump, and the current separate starter and dump step names already exposed from `zigux/tests/build.zig`. It does not claim runtime pointer dereference behavior, export-shim wiring, broader UAPI layout support, IDR or IDA coverage, or the still-missing combined shared `phase3-errptr-xarray` route.
