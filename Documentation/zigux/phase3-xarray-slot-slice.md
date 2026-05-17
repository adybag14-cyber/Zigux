# Phase 3 xarray slot Slice

This note records one bounded Phase 3 helper-side interop slice on current `master`.

## Current Slice

- `zigux/helpers/xarray_slot_view.zig`
- `zigux/tests/phase3_xarray_slot_starter_packet.zig`
- `zigux/tests/phase3_xarray_slot_starter_packet_build.zig`
- `scripts/zigux/check-phase3-xarray-slot-starter-packet.py`
- `zigux/tests/phase3_xarray_slot_dump.zig`
- `zigux/tests/phase3_xarray_slot_dump_build.zig`
- `zigux/tests/fixtures/phase3_xarray_slot/phase3_xarray_slot_c_harness.c`
- `zigux/tests/fixtures/phase3_xarray_slot/expected.json`
- `zigux/tests/fixtures/phase3_xarray_slot_manifest.json`
- `scripts/zigux/check-phase3-xarray-slot.py`

## Bounded Contract

The helper stays intentionally small:

- `zigux/helpers/xarray_slot_view.zig` only classifies raw slot words as null, inline `xa_value`, tagged `err_ptr`, or ordinary pointer-like entries
- it reuses the already-landed `zigux/helpers/err_ptr.zig` and `zigux/helpers/xa_value.zig` helpers instead of assuming the broader Phase 3 ABI packet is already present on current `master`
- `zigux/tests/phase3_xarray_slot_starter_packet.zig` proves that null slots, tagged inline values, tagged error entries, and ordinary pointer-like values stay disjoint

## Current Replay Surface

The current helper-local packet now has two bounded replay layers:

- one direct starter packet:
  - `zigux/tests/phase3_xarray_slot_starter_packet.zig`
  - `zigux/tests/phase3_xarray_slot_starter_packet_build.zig`
  - `scripts/zigux/check-phase3-xarray-slot-starter-packet.py`
  - `python3 scripts/zigux/check-phase3-xarray-slot-starter-packet.py --self-test`
  - `python3 scripts/zigux/check-phase3-xarray-slot-starter-packet.py`
- one fixture-backed parity packet:
  - `zigux/tests/phase3_xarray_slot_dump.zig`
  - `zigux/tests/phase3_xarray_slot_dump_build.zig`
  - `zigux/tests/fixtures/phase3_xarray_slot/phase3_xarray_slot_c_harness.c`
  - `zigux/tests/fixtures/phase3_xarray_slot/expected.json`
  - `zigux/tests/fixtures/phase3_xarray_slot_manifest.json`
  - `scripts/zigux/check-phase3-xarray-slot.py`
  - `python3 scripts/zigux/check-phase3-xarray-slot.py --self-test`
  - `python3 scripts/zigux/check-phase3-xarray-slot.py --repo-root . --zig zig --cc gcc`
  - `zig build phase3-xarray-slot-dump --build-file zigux/tests/phase3_xarray_slot_dump_build.zig`

That fixture-backed parity packet keeps one tiny C-vs-Zig xarray-slot comparison explicit without reopening the broader shared tests root.

## Current Gap

This is still not the broader Phase 3 ABI, export/UAPI, catalog, IDR, or IDA packet that older reminder surfaces still name. It is one helper-local xarray follow-on layered beside the existing `err_ptr` / `xarray` slice.

Current shared reminder follow-up still belongs to the broader Phase 3 truthfulness pass:

- `Documentation/zigux/README.md`
- `zigux/tests/README.md`
- `Documentation/zigux/review-checklist.md`

Those surfaces should stay aligned with the bounded starter packet plus helper-local slices instead of treating the wider validator, export-boundary, or slot-family routes as shipped proof on current `master`.

## Scope

This note is limited to helper-local slot classification plus one tiny fixture-backed parity dump. It does not claim xarray node walking, IDR or IDA coverage, runtime pointer dereference behavior, export-shim wiring, broader UAPI layout support, or any shared `phase3` replay route.