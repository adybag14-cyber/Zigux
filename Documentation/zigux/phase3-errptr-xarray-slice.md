# Phase 3 err_ptr/xarray Slice

This note records one bounded Phase 3 helper-side interop slice on current `master`.

## Current Slice

- `zigux/helpers/err_ptr.zig`
- `zigux/helpers/xa_value.zig`
- `zigux/helpers/xarray_slot_view.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`
- `zigux/tests/phase3_xarray_slot_starter_packet.zig`
- `zigux/tests/build.zig`
- `scripts/zigux/check-phase3-xarray-slot-starter-packet.py`
- `zigux/tests/phase3_errptr_xarray_dump.zig`
- `zigux/tests/phase3_errptr_xarray_dump_build.zig`
- `zigux/tests/fixtures/phase3_errptr_xarray/phase3_errptr_xarray_c_harness.c`
- `zigux/tests/fixtures/phase3_errptr_xarray/expected.json`
- `zigux/tests/fixtures/phase3_errptr_xarray_manifest.json`
- `scripts/zigux/check-phase3-errptr-xarray.py`

## Bounded Contract

The helper packet stays intentionally small:

- `zigux/helpers/err_ptr.zig` only models the Linux `MAX_ERRNO` tag band as a pointer-sized integer encoding
- `zigux/helpers/xa_value.zig` only models the low-bit inline-value tag and rejects values that would enter the `err_ptr` band
- `zigux/helpers/xarray_slot_view.zig` keeps null, inline-value, `err_ptr`, and pointer-like xarray slot lanes explicit on top of those two tagged encodings without widening into ownership, dereference, or broader xarray traversal semantics
- `zigux/tests/phase3_errptr_xarray_starter_packet.zig` proves that accepted inline values round-trip cleanly, that the highest tagged inline boundary still stays below the `err_ptr` floor, and that overlapping encodings fail closed
- `zigux/tests/phase3_xarray_slot_starter_packet.zig` proves that null, value, error, and pointer-like slot lanes stay explicit without collapsing tagged internal entries back into pointer-like state

## Current Replay Surface

The current helper-local packet now has three bounded replay layers:

- one manifest-backed starter packet:
  - `zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json`
  - `scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`
  - `python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py --self-test`
  - `python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`
- one shared tests-root xarray-slot starter packet:
  - `zigux/helpers/xarray_slot_view.zig`
  - `zigux/tests/phase3_xarray_slot_starter_packet.zig`
  - `zigux/tests/build.zig`
  - `scripts/zigux/check-phase3-xarray-slot-starter-packet.py`
  - `python3 scripts/zigux/check-phase3-xarray-slot-starter-packet.py --self-test`
  - `python3 scripts/zigux/check-phase3-xarray-slot-starter-packet.py`
  - `zig build phase3-xarray-slot-starter-packet --build-file zigux/tests/build.zig`
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

That keeps one helper-local tagged-value starter packet, one xarray-slot lane classifier starter packet, and one tiny C-vs-Zig parity packet explicit without reopening the broader shared tests root.

## Current Gap

This is still not the broader Phase 3 ABI, export/UAPI, catalog, or low-level-wrapper packet that older reminder surfaces still name. It is one helper-local interop proof layered beside the existing `dev_t` starter packet.

The earlier shared reminder follow-up is now closed across the docs root, review checklist, and tests root on current `master`:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `zigux/tests/README.md`
- `Documentation/zigux/phase3-validator-support-surface.md`
- `Documentation/zigux/phase3-shared-reminder-gap.md`

Those surfaces now keep the bounded three-slice posture explicit while this helper-local note also keeps the landed `xarray_slot_view` starter packet visible inside the existing `err_ptr` / `xarray` lane. Any future follow-up from this helper-local slice should stay limited to `err_ptr` / `xa_value` / `xarray_slot_view` packet truthfulness or separate scripts-root inventory drift, not treat the closed shared-reminder cleanup as evidence that the wider validator or export-boundary routes already ship on `master`.

## Scope

This note is limited to the helper-local `err_ptr`, `xa_value`, and `xarray_slot_view` tagged-value boundary together with one tiny fixture-backed parity dump. It does not claim runtime pointer dereference behavior, export-shim wiring, broader UAPI layout support, IDR or IDA coverage, or any shared `phase3` replay route.
