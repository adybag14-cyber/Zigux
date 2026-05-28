# Phase 3 idr-slot Slice

This note records one bounded Phase 3 helper-side `idr_slot` packet on current `master`.

## Current Slice

- `zigux/helpers/err_ptr.zig`
- `zigux/helpers/xa_value.zig`
- `zigux/helpers/xarray_slot_view.zig`
- `zigux/helpers/idr_slot_view.zig`
- `zigux/tests/phase3_idr_slot_starter_packet.zig`
- `zigux/tests/phase3_idr_slot_starter_packet_build.zig`
- `zigux/tests/phase3_idr_slot_dump.zig`
- `zigux/tests/phase3_idr_slot_dump_build.zig`
- `zigux/tests/fixtures/phase3_idr_slot/phase3_idr_slot_c_harness.c`
- `zigux/tests/fixtures/phase3_idr_slot/expected.json`
- `zigux/tests/fixtures/phase3_idr_slot_manifest.json`
- `scripts/zigux/check-phase3-idr-slot-starter-packet.py`
- `scripts/zigux/check-phase3-idr-slot.py`
- `zigux/Makefile`

## Bounded Contract

This packet stays intentionally small:

- `zigux/helpers/idr_slot_view.zig` only classifies one raw IDR slot word into four bounded lanes: `empty`, tagged internal `xa_value`, tagged `err_ptr`, and pointer-backed.
- The helper reuses the already-landed `xarray_slot_view`, `xa_value`, and `err_ptr` rules instead of widening into allocation, traversal, ownership, or broader IDR semantics.
- `zigux/tests/phase3_idr_slot_starter_packet.zig` keeps the empty, pointer, tagged-value, tagged-error, and top-of-error-band cases explicit so the tagged encodings do not drift back into the pointer lane.
- `zigux/tests/phase3_idr_slot_dump.zig` plus the matching C harness replay the same bounded slot classifications and raw encodings as a tiny parity packet instead of widening into the broader ABI dump family.
- `zigux/Makefile` exposes one focused starter-packet wrapper and one focused dump wrapper so the helper-local rerun surface stays reachable without widening into the aggregate shared Phase 3 lane.
- The manifest and both checkers keep this as a helper-local starter-plus-dump packet rather than claiming the wider shared ABI validator, xarray dump parity surface, or the broader IDA follow-through.

## Current Replay Surface

The current helper-local packet now has two bounded replay layers:

- one starter packet:
  - `zigux/helpers/idr_slot_view.zig`
  - `zigux/tests/phase3_idr_slot_starter_packet.zig`
  - `zigux/tests/phase3_idr_slot_starter_packet_build.zig`
  - `zigux/tests/fixtures/phase3_idr_slot_manifest.json`
  - `scripts/zigux/check-phase3-idr-slot-starter-packet.py`
  - `python3 scripts/zigux/check-phase3-idr-slot-starter-packet.py --self-test`
  - `python3 scripts/zigux/check-phase3-idr-slot-starter-packet.py --repo-root .`
  - `zig build phase3-idr-slot-starter-packet-test --build-file zigux/tests/phase3_idr_slot_starter_packet_build.zig`
  - `make -C zigux phase3-idr-slot-starter-packet-test`
- one fixture-backed dump parity packet:
  - `zigux/tests/phase3_idr_slot_dump.zig`
  - `zigux/tests/phase3_idr_slot_dump_build.zig`
  - `zigux/tests/fixtures/phase3_idr_slot/phase3_idr_slot_c_harness.c`
  - `zigux/tests/fixtures/phase3_idr_slot/expected.json`
  - `scripts/zigux/check-phase3-idr-slot.py`
  - `python3 scripts/zigux/check-phase3-idr-slot.py --self-test`
  - `python3 scripts/zigux/check-phase3-idr-slot.py --repo-root . --zig zig --cc gcc`
  - `zig build phase3-idr-slot-dump --build-file zigux/tests/phase3_idr_slot_dump_build.zig`
  - `make -C zigux phase3-idr-slot-dump`

That keeps the current follow-through narrow and reviewable without reopening the broader shared Phase 3 validator packet.

## Current Gap

This is still not the broader shared Phase 3 catalog or validator-support packet. The landed `idr_slot` helper-local starter-plus-dump packet is real repo evidence, but any same-lane follow-through should stay narrowed to shared-validator alignment or the separate IDA family only after a fresh reread of current `master`.

## Scope

This note is limited to the helper-local `idr_slot_view` classifier layered on the already-landed tagged `xarray_slot_view`, `xa_value`, and `err_ptr` helpers, together with one starter packet, one fixture-backed dump parity packet, one dedicated dump build file, one helper-local manifest, two focused Makefile wrappers, and two checkers. It does not claim broader IDR traversal semantics, export-shim wiring, xarray dump parity outside this packet, or wider IDA coverage.
