# Phase 1 Bitmap Survey

Lane: `P1-L01`

## Scope

This note surveys the current `tools/lib/bitmap.zig` lane against the Phase 1 roadmap target and the bootstrap commit ledger.

## Roadmap And Ledger Expectation

Phase 1 in `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md` names `tools/lib/bitmap.c` as one of the low-risk host-side helper targets whose Zigux destination should live in `tools/lib/bitmap.zig`.

The same roadmap's commit train and `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md` reduce that to two bounded promises for bitmap:

- land the Phase 1 host-side helper port in `tools/lib/bitmap.zig`
- keep the helper inside the golden-output Phase 1 parity packet instead of treating it as an unreviewed standalone port

## Current Master Reality

Current `master` satisfies the bounded Phase 1 bitmap port itself:

- `tools/lib/bitmap.zig` exists and now carries the expected host-helper surface plus direct Zig unit anchors for allocator sizing, range mutation, predicate masking, copy aliases, range rendering, zero-bit behavior, and Linux-style bitmap aliases
- `zigux/tests/phase1_helpers.zig` replays shared bitmap fixture fields for weight, boolean binary operations, range rendering, truncation, tiny-buffer handling, partial-window xor masking, and empty or full transitions
- `zigux/tests/fixtures/phase1_helpers.json` commits those shared bitmap parity values
- `zigux/tests/fixtures/phase1_helper_manifest.json` records the current bitmap review anchors and explicitly keeps `tools/lib/bitmap.zig` in the direct-anchor follow-up set rather than the parked shared-replay-only helper set
- `Documentation/zigux/phase1-closure.md` already treats bitmap as part of the closed Phase 1 helper packet and names the helper-local review obligations that still need to stay visible when bitmap changes

## Gap Summary

There is no missing Phase 1 bitmap port gap left relative to the roadmap or the ledger. The original roadmap ask for a host-side helper port plus a shared parity route is already present on current `master`.

The real current-state gap was helper-lane truthfulness drift: the repo had the closed shared packet, the live helper-local anchors, and the Phase 1 closure review rule, but the bitmap-specific survey note understated which direct anchors still belong to `tools/lib/bitmap.zig` on current `master`.

That direct-anchor follow-up remains legitimate because the shared Phase 1 replay does not fully subsume every bitmap-local behavior. Current `master` still relies on helper-local anchors for:

- allocator sizing, zero-fill, and empty-buffer handling
- exact first-word and final-partial-word range boundaries plus last-word tail clamping
- predicate tail masking beyond `nbits`
- cross-word `bitmap.scnprintf()` collapse, truncation, and empty-buffer behavior
- raw copy versus tail-clearing copy alias behavior plus zero-and-aligned copy-extension behavior
- zero-bit no-op behavior and zero-bit binary identity behavior
- Linux-style alias lockstep across alloc or free, mutation, predicate, copy, and render entrypoints

The shared Phase 1 replay still owns the committed rendered bitmap string, tiny-buffer `scnprintf()` fixture keys, partial-window xor masking, and the basic boolean operation outputs. The direct helper-local anchors remain the bounded proof for the rest of the bitmap surface above.

## Lane Decision

Keep this lane parked as a Phase 1 survey and truthfulness lane, not as a reopen-Phase-1 implementation lane.

The next safe bitmap-only step is review-surface maintenance rather than new helper work: if `tools/lib/bitmap.zig` changes again, keep the direct helper-local anchors and the shared Phase 1 fixture packet aligned instead of widening Phase 1 scope or inventing a new bitmap tranche.

When `tools/lib/bitmap.zig` changes again, the bounded follow-up should stay inside one of two surfaces only:

- the shared Phase 1 replay packet in `zigux/tests/phase1_helpers.zig`, `zigux/tests/fixtures/phase1_helpers.json`, and `zigux/tests/fixtures/phase1_helper_manifest.json`
- the existing helper-local direct anchors inside `tools/lib/bitmap.zig`

Any future bitmap work should preserve that ownership split unless the shared replay is deliberately expanded enough to retire one of the current helper-local anchors.
