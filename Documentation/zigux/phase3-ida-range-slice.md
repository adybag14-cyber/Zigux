# Phase 3 ida-range Slice

This note records one bounded Phase 3 helper-local ida range packet on current work for the shared-subsystems lane.

## Current Slice

- `zigux/helpers/ida_bitmap_view.zig`
- `zigux/helpers/ida_alloc_view.zig`
- `zigux/helpers/ida_range_view.zig`
- `zigux/tests/phase3_ida_range_starter_packet.zig`
- `zigux/tests/phase3_ida_range_starter_packet_build.zig`
- `scripts/zigux/check-phase3-ida-range-starter-packet.py`
- `zigux/tests/phase3_ida_range_dump.zig`
- `zigux/tests/phase3_ida_range_dump_build.zig`
- `zigux/tests/fixtures/phase3_ida_range/phase3_ida_range_c_harness.c`
- `zigux/tests/fixtures/phase3_ida_range/expected.json`
- `zigux/tests/fixtures/phase3_ida_range_manifest.json`
- `scripts/zigux/check-phase3-ida-range.py`

## Bounded Contract

This helper-local ida range packet stays intentionally small:

- `zigux/helpers/ida_range_view.zig` only clamps one requested range into one fixed `ida_bitmap` chunk and summarizes the bounded window with allocation counts plus first-allocated and first-free positions.
- The helper does not claim broader IDA ownership, multi-chunk stitching, allocator locking, or policy semantics.
- `zigux/tests/phase3_ida_range_starter_packet.zig` keeps floor clamping, ceiling clamping, partial windows, clear windows, and invalid-window rejection explicit.
- `zigux/tests/phase3_ida_range_dump.zig` plus the matching C harness replay the same bounded range summaries as one tiny Zig-vs-C parity packet instead of widening into the broader shared ABI validator.

## Current Replay Surface

The current helper-local ida range packet now has two bounded replay layers:

- one starter packet:
  `zigux/tests/phase3_ida_range_starter_packet.zig`
  `zigux/tests/phase3_ida_range_starter_packet_build.zig`
  `scripts/zigux/check-phase3-ida-range-starter-packet.py`
  `python3 scripts/zigux/check-phase3-ida-range-starter-packet.py --self-test`
  `python3 scripts/zigux/check-phase3-ida-range-starter-packet.py`
  `zig build phase3-ida-range-starter-packet-test --build-file zigux/tests/phase3_ida_range_starter_packet_build.zig`
- one fixture-backed dump parity packet:
  `zigux/tests/phase3_ida_range_dump.zig`
  `zigux/tests/phase3_ida_range_dump_build.zig`
  `zigux/tests/fixtures/phase3_ida_range/phase3_ida_range_c_harness.c`
  `zigux/tests/fixtures/phase3_ida_range/expected.json`
  `zigux/tests/fixtures/phase3_ida_range_manifest.json`
  `scripts/zigux/check-phase3-ida-range.py`
  `python3 scripts/zigux/check-phase3-ida-range.py --self-test`
  `python3 scripts/zigux/check-phase3-ida-range.py --repo-root . --zig zig --cc gcc`
  `zig build phase3-ida-range-dump --build-file zigux/tests/phase3_ida_range_dump_build.zig`

## Current Gap

This is still not the broader shared Phase 3 ABI packet and not the later `ida_policy` follow-through. The landed helper-local ida range packet is real repo evidence, but any same-lane follow-through should stay narrowed to dump parity, shared-manifest alignment, or the next IDA helper family after rereading current `master`.

## Scope

This note is limited to the helper-local ida range packet layered on the already-landed `ida_bitmap` and `ida_alloc` helpers, together with one starter packet, one dump parity replay, one manifest, and one checker pair. It does not claim broader allocator lifecycle, ABI export-shim wiring, or wider IDA completion.
