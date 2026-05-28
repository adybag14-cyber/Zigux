# Phase 3 ida-bitmap Slice

This note records one bounded Phase 3 helper-side `ida_bitmap` starter packet on current work for the shared-subsystems lane.

## Current Slice

- `zigux/helpers/ida_bitmap_view.zig`
- `zigux/tests/phase3_ida_bitmap_starter_packet.zig`
- `zigux/tests/phase3_ida_bitmap_starter_packet_build.zig`
- `zigux/tests/phase3_ida_bitmap_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-ida-bitmap-starter-packet.py`

## Bounded Contract

This packet stays intentionally small:

- `zigux/helpers/ida_bitmap_view.zig` only describes one fixed 128-byte IDA bitmap chunk and the bounded first-set, first-zero, empty, full, and weight helpers around that chunk.
- `zigux/tests/phase3_ida_bitmap_starter_packet.zig` keeps the fixed chunk geometry, empty chunk, sparse cross-word bits, full chunk exhaustion, and partial-word first-zero behavior explicit without widening into allocation, policy, or range semantics.
- the manifest and checker keep this as a helper-local starter packet rather than claiming the broader shared ABI validator or the later `ida_alloc`, `ida_range`, or `ida_policy` follow-through.

## Current Replay Surface

The current helper-local packet now has one bounded replay layer:

- `zigux/helpers/ida_bitmap_view.zig`
- `zigux/tests/phase3_ida_bitmap_starter_packet.zig`
- `zigux/tests/phase3_ida_bitmap_starter_packet_build.zig`
- `zigux/tests/phase3_ida_bitmap_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-ida-bitmap-starter-packet.py`
- `python3 scripts/zigux/check-phase3-ida-bitmap-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-ida-bitmap-starter-packet.py`
- `zig build phase3-ida-bitmap-starter-packet-test --build-file zigux/tests/phase3_ida_bitmap_starter_packet_build.zig`

## Current Gap

This is still not the broader shared Phase 3 ABI catalog or the later IDA allocation and range slices from the roadmap. The landed `ida_bitmap` helper-local starter packet is real repo evidence, but any same-lane follow-through should stay narrowed to dump parity or the separate IDA helper families only after a fresh reread of current `master`.

## Scope

This note is limited to the helper-local `ida_bitmap_view` chunk helper together with one starter packet, one dedicated build file, one helper-local manifest, and one checker. It does not claim broader IDA allocation behavior, export-shim wiring, or wider shared ABI coverage.
