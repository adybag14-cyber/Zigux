# Phase 3 xarray slot Slice

This note records the current helper-local Phase 3 `xarray_slot` interop slice on current `master`.

## Current Slice

- `Documentation/zigux/phase3-errptr-xarray-slice.md`
- `zigux/helpers/err_ptr.zig`
- `zigux/helpers/xa_value.zig`
- `zigux/helpers/xarray_slot_view.zig`
- `zigux/tests/phase3_xarray_slot_starter_packet.zig`
- `zigux/tests/phase3_xarray_slot_starter_packet_build.zig`
- `scripts/zigux/check-phase3-xarray-slot-starter-packet.py`
- `zigux/tests/build.zig`
- `zigux/tests/phase3_xarray_slot_dump.zig`
- `zigux/tests/phase3_xarray_slot_dump_build.zig`
- `zigux/tests/fixtures/phase3_xarray_slot/phase3_xarray_slot_c_harness.c`
- `zigux/tests/fixtures/phase3_xarray_slot/expected.json`
- `zigux/tests/fixtures/phase3_xarray_slot_manifest.json`
- `scripts/zigux/check-phase3-xarray-slot.py`

## Bounded Contract

This packet stays intentionally small:

- `zigux/helpers/xarray_slot_view.zig` only classifies one raw slot word into four bounded lanes: `null`, tagged `xa_value`, tagged `err_ptr`, and pointer-like.
- The helper builds only on the already-landed `zigux/helpers/err_ptr.zig` and `zigux/helpers/xa_value.zig` tagged-value rules; it does not claim ownership, dereference, traversal, or broader xarray semantics.
- `zigux/tests/phase3_xarray_slot_starter_packet.zig` keeps the null, inline-zero, inline-limit, error, and ordinary pointer-like cases explicit so the tagged-value floor never collapses back into the pointer lane.
- `zigux/tests/phase3_xarray_slot_dump.zig` plus the matching C harness replay the same bounded slot classifications and raw encodings as a tiny parity packet instead of widening into the broader ABI dump family.

## Current Replay Surface

The current helper-local packet now has two bounded replay layers:

- one starter packet:
  - `zigux/helpers/xarray_slot_view.zig`
  - `zigux/tests/phase3_xarray_slot_starter_packet.zig`
  - `zigux/tests/phase3_xarray_slot_starter_packet_build.zig`
  - `scripts/zigux/check-phase3-xarray-slot-starter-packet.py`
  - `python3 scripts/zigux/check-phase3-xarray-slot-starter-packet.py --self-test`
  - `python3 scripts/zigux/check-phase3-xarray-slot-starter-packet.py --repo-root .`
  - `zig build phase3-xarray-slot-starter-packet-test --build-file zigux/tests/phase3_xarray_slot_starter_packet_build.zig`
  - `zigux/tests/build.zig`
  - `zig build phase3-xarray-slot-starter-packet --build-file zigux/tests/build.zig`
- one fixture-backed dump parity packet:
  - `zigux/tests/phase3_xarray_slot_dump.zig`
  - `zigux/tests/phase3_xarray_slot_dump_build.zig`
  - `zigux/tests/fixtures/phase3_xarray_slot/phase3_xarray_slot_c_harness.c`
  - `zigux/tests/fixtures/phase3_xarray_slot/expected.json`
  - `zigux/tests/fixtures/phase3_xarray_slot_manifest.json`
  - `scripts/zigux/check-phase3-xarray-slot.py`
  - `python3 scripts/zigux/check-phase3-xarray-slot.py --self-test`
  - `python3 scripts/zigux/check-phase3-xarray-slot.py --repo-root . --zig zig --cc gcc`
  - `zig build phase3-xarray-slot-dump --build-file zigux/tests/phase3_xarray_slot_dump_build.zig`

That keeps one shared-tests-root starter hook and one tiny C-vs-Zig parity replay explicit without reopening the broader shared validator, export/UAPI survey, or catalog packet.

## Current Gap

This is still not the broader Phase 3 shared validator-support packet. `zigux/tests/fixtures/phase3_xarray_slot_manifest.json` now treats `Documentation/zigux/phase3-xarray-slot-slice.md` as the missing docs-root follow-through while still listing `Documentation/zigux/phase3-validator-support-surface.md` and `scripts/zigux/validate-phase3.py` as separate repo-reality gaps for this helper-local packet.

That means the landed `xarray_slot` helper, starter checker, dump checker, and fixture-backed parity packet are real current-`master` evidence, but they should stay helper-local until a fresh same-lane reread decides whether the broader validator-support note or shared validator entrypoint should absorb them. This note should not be used to imply that the broader Phase 3 export/UAPI survey, shared replay packet, catalog wiring, IDR family, or IDA family has returned.

## Scope

This note is limited to the helper-local `xarray_slot_view` classifier layered on the already-landed `err_ptr` and `xa_value` helpers, together with one starter packet and one fixture-backed dump parity replay. It does not claim broader shared validator support, runtime dereference behavior, export-shim wiring, UAPI layout completion, or wider xarray, IDR, or IDA coverage.
