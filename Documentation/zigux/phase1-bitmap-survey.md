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

- `tools/lib/bitmap.zig` exists and now carries the expected host-helper surface plus direct Zig unit anchors for allocator sizing, range mutation, predicate masking, copy aliases, zero-bit behavior, and Linux-style bitmap aliases
- `zigux/tests/phase1_helpers.zig` replays shared bitmap fixture fields for weight, boolean binary operations, range rendering, truncation, tiny-buffer handling, partial-window xor masking, and empty or full transitions
- `zigux/tests/fixtures/phase1_helpers.json` commits those shared bitmap parity values
- `zigux/tests/fixtures/phase1_helper_manifest.json` records the current bitmap review anchors and explicitly keeps `tools/lib/bitmap.zig` in the direct-anchor follow-up set rather than the parked shared-replay-only helper set
- `Documentation/zigux/phase1-closure.md` already treats bitmap as part of the closed Phase 1 helper packet and names the helper-local review obligations that still need to stay visible when bitmap changes

## Gap Summary

There is no missing Phase 1 bitmap port gap left relative to the roadmap or the ledger. The original roadmap ask for a host-side helper port plus a shared parity route is already present on current `master`.

The real current-state gap was documentation truthfulness at the helper-lane level: the repo had the closed shared packet and the live helper-local anchors, but it did not have a bitmap-specific survey note saying that Phase 1 is closed while `tools/lib/bitmap.zig` still owns bounded direct follow-up anchors.

That direct-anchor follow-up remains legitimate because the shared Phase 1 replay does not fully subsume every bitmap-local behavior. Current `master` still relies on helper-local anchors for:

- allocator sizing and zero-fill behavior
- exact first-word and final-partial-word range boundaries
- predicate tail masking beyond `nbits`
- raw copy versus tail-clearing copy alias behavior
- zero-bit no-op and zero-bit identity behavior
- Linux-style alias lockstep across the helper surface

## Lane Decision

Keep this lane parked as a Phase 1 survey and truthfulness lane, not as a reopen-Phase-1 implementation lane.

When `tools/lib/bitmap.zig` changes again, the bounded follow-up should stay inside one of two surfaces only:

- the shared Phase 1 replay packet in `zigux/tests/phase1_helpers.zig`, `zigux/tests/fixtures/phase1_helpers.json`, and `zigux/tests/fixtures/phase1_helper_manifest.json`
- the existing helper-local direct anchors inside `tools/lib/bitmap.zig`

Any future bitmap work should preserve that ownership split unless the shared replay is deliberately expanded enough to retire one of the current helper-local anchors.
