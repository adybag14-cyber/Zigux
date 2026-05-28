# Phase 3 ida-alloc Slice

This note records one bounded Phase 3 helper-local ida allocation packet on current work for the shared-subsystems lane.

## Current Slice

- `zigux/helpers/ida_bitmap_view.zig`
- `zigux/helpers/ida_alloc_view.zig`
- `zigux/tests/phase3_ida_alloc_starter_packet.zig`
- `zigux/tests/phase3_ida_alloc_starter_packet_build.zig`
- `scripts/zigux/check-phase3-ida-alloc-starter-packet.py`
- `zigux/tests/phase3_ida_alloc_dump.zig`
- `zigux/tests/phase3_ida_alloc_dump_build.zig`
- `zigux/tests/fixtures/phase3_ida_alloc/phase3_ida_alloc_c_harness.c`
- `zigux/tests/fixtures/phase3_ida_alloc/expected.json`
- `zigux/tests/fixtures/phase3_ida_alloc_manifest.json`
- `scripts/zigux/check-phase3-ida-alloc.py`

## Bounded Contract

This helper-local ida allocation packet stays intentionally small:

- `zigux/helpers/ida_alloc_view.zig` only maps one fixed `ida_bitmap` chunk into chunk-relative allocation windows and first-free selection.
- The helper does not claim broader IDA ownership, global multi-chunk search, allocator locking, or policy semantics.
- `zigux/tests/phase3_ida_alloc_starter_packet.zig` keeps sparse allocation, chunk-floor clamping, chunk-ceiling clamping, disjoint windows, and ordered-range rejection explicit.
- `zigux/tests/phase3_ida_alloc_dump.zig` plus the matching C harness replay the same bounded allocation-window decisions as one tiny Zig-vs-C parity packet instead of widening into the broader shared ABI validator.

## Current Replay Surface

The current helper-local ida allocation packet now has two bounded replay layers:

- one starter packet:
  `zigux/tests/phase3_ida_alloc_starter_packet.zig`
  `zigux/tests/phase3_ida_alloc_starter_packet_build.zig`
  `scripts/zigux/check-phase3-ida-alloc-starter-packet.py`
  `python3 scripts/zigux/check-phase3-ida-alloc-starter-packet.py --self-test`
  `python3 scripts/zigux/check-phase3-ida-alloc-starter-packet.py`
  `zig build phase3-ida-alloc-starter-packet-test --build-file zigux/tests/phase3_ida_alloc_starter_packet_build.zig`
- one fixture-backed dump parity packet:
  `zigux/tests/phase3_ida_alloc_dump.zig`
  `zigux/tests/phase3_ida_alloc_dump_build.zig`
  `zigux/tests/fixtures/phase3_ida_alloc/phase3_ida_alloc_c_harness.c`
  `zigux/tests/fixtures/phase3_ida_alloc/expected.json`
  `zigux/tests/fixtures/phase3_ida_alloc_manifest.json`
  `scripts/zigux/check-phase3-ida-alloc.py`
  `python3 scripts/zigux/check-phase3-ida-alloc.py --self-test`
  `python3 scripts/zigux/check-phase3-ida-alloc.py --repo-root . --zig zig --cc gcc`
  `zig build phase3-ida-alloc-dump --build-file zigux/tests/phase3_ida_alloc_dump_build.zig`

## Current Gap

This is still not the broader shared Phase 3 ABI packet and not the later `ida_range` or `ida_policy` follow-through. The landed helper-local ida allocation packet is real repo evidence, but any same-lane follow-through should stay narrowed to dump parity, shared-manifest alignment, or the next IDA helper family after rereading current `master`.

## Scope

This note is limited to the helper-local ida allocation packet layered on the already-landed fixed `ida_bitmap` chunk helper, together with one starter packet, one dump parity replay, one manifest, and one checker pair. It does not claim broader allocator lifecycle, ABI export-shim wiring, or wider IDA completion.
