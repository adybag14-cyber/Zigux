# Phase 3 ida-slot Slice

This note records one bounded Phase 3 helper-side `ida_slot` packet on current `master`.

## Current Slice

- `zigux/helpers/err_ptr.zig`
- `zigux/helpers/xa_value.zig`
- `zigux/helpers/xarray_slot_view.zig`
- `zigux/helpers/ida_slot_view.zig`
- `zigux/tests/phase3_ida_slot_starter_packet.zig`
- `zigux/tests/phase3_ida_slot_starter_packet_build.zig`
- `zigux/tests/phase3_ida_slot_dump.zig`
- `zigux/tests/phase3_ida_slot_dump_build.zig`
- `zigux/tests/fixtures/phase3_ida_slot/phase3_ida_slot_c_harness.c`
- `zigux/tests/fixtures/phase3_ida_slot/expected.json`
- `zigux/tests/fixtures/phase3_ida_slot_manifest.json`
- `scripts/zigux/check-phase3-ida-slot-starter-packet.py`
- `scripts/zigux/check-phase3-ida-slot.py`

## Bounded Contract

This packet stays intentionally small:

- `zigux/helpers/ida_slot_view.zig` only classifies one raw IDA xarray entry into four bounded lanes: `empty`, tagged inline bits, bitmap pointer, and defensive unexpected `err_ptr`.
- The helper reuses the already-landed `xarray_slot_view` and `xa_value` rules instead of widening into allocation, traversal, bitmap ownership, or broader IDA semantics.
- `zigux/tests/phase3_ida_slot_starter_packet.zig` keeps the empty, inline-mask, pointer-backed, and impossible tagged-error cases explicit so inline bit packs do not drift into the pointer lane.
- `zigux/tests/phase3_ida_slot_dump.zig` plus the matching C harness replay the same bounded classifications and decoded inline-mask summaries as a tiny parity packet instead of widening into the broader shared ABI dump family.
- The manifest and both checkers keep this as a helper-local starter-plus-dump packet rather than claiming the wider shared validator, bitmap traversal, or IDR/IDA allocation follow-through.

## Current Replay Surface

The current helper-local packet has two bounded replay layers:

- one starter packet:
  - `zigux/helpers/ida_slot_view.zig`
  - `zigux/tests/phase3_ida_slot_starter_packet.zig`
  - `zigux/tests/phase3_ida_slot_starter_packet_build.zig`
  - `zigux/tests/fixtures/phase3_ida_slot_manifest.json`
  - `scripts/zigux/check-phase3-ida-slot-starter-packet.py`
  - `python3 scripts/zigux/check-phase3-ida-slot-starter-packet.py --self-test`
  - `python3 scripts/zigux/check-phase3-ida-slot-starter-packet.py --repo-root .`
  - `zig build phase3-ida-slot-starter-packet-test --build-file zigux/tests/phase3_ida_slot_starter_packet_build.zig`
- one fixture-backed dump parity packet:
  - `zigux/tests/phase3_ida_slot_dump.zig`
  - `zigux/tests/phase3_ida_slot_dump_build.zig`
  - `zigux/tests/fixtures/phase3_ida_slot/phase3_ida_slot_c_harness.c`
  - `zigux/tests/fixtures/phase3_ida_slot/expected.json`
  - `scripts/zigux/check-phase3-ida-slot.py`
  - `python3 scripts/zigux/check-phase3-ida-slot.py --self-test`
  - `python3 scripts/zigux/check-phase3-ida-slot.py --repo-root . --zig zig --cc gcc`
  - `zig build phase3-ida-slot-dump --build-file zigux/tests/phase3_ida_slot_dump_build.zig`

That keeps the current follow-through narrow and reviewable without reopening the broader shared Phase 3 validator packet.

## Current Gap

This is still not the broader shared Phase 3 catalog or validator-support packet. The landed `ida_slot` helper-local starter-plus-dump packet is real repo evidence, but any same-lane follow-through should stay narrowed to shared-validator alignment after a fresh reread of current `master`.

## Scope

This note is limited to the helper-local `ida_slot_view` classifier layered on the already-landed tagged `xarray_slot_view` and `xa_value` helpers, together with one starter packet, one fixture-backed dump parity packet, one helper-local manifest, and two checkers. It does not claim broader IDA allocation semantics, bitmap dereference behavior, export-shim wiring, or wider shared validator completion.
