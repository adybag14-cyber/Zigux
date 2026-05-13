# Phase 1 Bitmap Size Alias Ownership

This note records one bounded helper-local ownership rule for `tools/lib/bitmap.zig`.

## Scope

- helper: `tools/lib/bitmap.zig`
- direct anchor: `test "bitmap size aliases round bit counts to full words in bytes"`
- packet boundary: Phase 1 host-side bitmap helper reviewability only

## Ownership Rule

The shared Phase 1 replay in `zigux/tests/phase1_helpers.zig` and `zigux/tests/fixtures/phase1_helpers.json` keeps allocator word counts explicit through `alloc_words` and `zalloc_words`, but it does not own the byte-count alias contract for `sizeBytes()` and `bitmap_size()`.

That direct helper-local test remains the bounded proof that:

- bit counts still round up to full-word storage in bytes
- `bitmap_size()` remains behaviorally locked to `sizeBytes()`
- zero-bit, single-word, aligned-word, and cross-word byte counts stay review-visible at the helper surface instead of being inferred indirectly from allocator paths

## Non-Goals

Do not widen this note into bitmap mutation, predicate, copy, or `scnprintf()` ownership. Those anchors already stay with the existing Phase 1 closure packet.
