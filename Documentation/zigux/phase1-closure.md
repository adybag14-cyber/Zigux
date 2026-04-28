# Phase 1 Closure

This document closes the bounded Phase 1 helper tranche for Zigux.

## Status

- `PHASE1_STATUS=closed`
- scope: counded host-side helper ports only
- product boundary: `tools/lib/*.zig`
- authority: current Linux C behavior remains the parity source

## Closed Helper Set

The bounded Phase 1 helper set is:

- `tools/lib/argv_split.zig`
- `tools/lib/bitmap.zig`
- `tools/lib/cmdline.zig`
- `tools/lib/ctype.zig`
- `tools/lib/find_bit.zig`
- `tools/lib/hweight.zig`
- `tools/lib/list_sort.zig`
- `tools/lib/rbtree.zig`
- `tools/lib/slab.zig`
- `tools/lib/str_error_r.zig`
- `tools/lib/string.zig`
- `tools/lib/vsprintf.zig`
- `tools/lib/zalloc.zig`

- `PHASE1_HELPER_COUNT=13`
- manifest: `zigux/tests/fixtures/phase1_helper_manifest.json`

No additional helper should be called Phase 1 work unless this document and the bootstrap validators are deliberately reopened.

## Helper Review Notes

- `tools/lib/bitmap.zig` closure includes committed C-backed parity coverage for contiguous-range rendering, partial-word bitmap copy behavior that leaves words beyond `nbits` untouched, the empty-bitmap buffer-preservation contract, and the truncation path that must preserve a trailing terminator slot.
- `tools/lib/bitmap.zig` direct Zig unit coverage now also keeps multiword-tail `xorBits` behavior aligned so callers can clamp the last word without leaking out-of-range bits into the asserted view.
- bitmap fixture authority: `zigux/tests/fixtures/phase1_helpers.json`
- bitmap manifest review anchor: `zigux/tests/fixtures/phase1_helper_manifest.json`
- bitmap direct unit-test anchor: `tools/lib/bitmap.zig:test "bitmap xor across a multiword tail still lets callers clamp the last word"`
- bitmap empty-bitmap review note: `bitmap_scnprintf` must leave a non-empty caller buffer untouched when no bits are set, matching the C helper contract

- `PHASE1_BITMAP_FIXTURE=zigux/tests/fixtures/phase1_helpers.json`
- `PHASE1_BITMAP_REVIEW=bitmap parity covers contiguous-range rendering, partial-word copy without clearing words beyond nbits, empty-bitmap buffer preservation, and truncation that preserves the terminator slot`
- `PHASE1_BITMAP_UNIT_REVIEW=bitmap multiword-tail xorBits behavior still lets callers clamp the last word without leaking out-of-range bits into the asserted view`