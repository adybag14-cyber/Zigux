# Phase 1 Bitmap Direct-Anchor Survey

This note records the lane-local survey for `tools/lib/bitmap.zig` against the Phase 1 roadmap and the bootstrap ledger. It does not reopen the closed Phase 1 helper tranche.

## Roadmap And Ledger Grounding

- roadmap phase: Phase 1 Alpha Host-Side Helpers
- roadmap target: `tools/lib/bitmap.c` with Zigux destination `tools/lib/bitmap.zig`
- required discipline: mixed-language helper build path, golden-output parity tests, and clear `.zig` ownership beside the C helper
- ledger anchor: `feat(tools/lib): start phase-1 helper ports` introduced `tools/lib/bitmap.zig`, and `test(zigux): add phase-1 helper harness and workflow gate` introduced the Phase 1 helper replay path

## Current Master Readback

Authenticated current-`master` reads during the lane survey recovered these bitmap-relevant anchors:

- `tools/lib/bitmap.zig` at blob `eb8e8cffd3d62e730ade1ede5ebe9324916ad781`
- `zigux/tests/fixtures/phase1_helper_manifest.json` at blob `ed5e9de4344916c5288f37271da2772113d99e6c`
- `Documentation/zigux/phase1-closure.md` at blob `78b2c440a409ef50bb245ad7a16f97b6454bab69`
- `Documentation/zigux/phase1-host-helper-lane-sequencing.md` at blob `383e61f14129022e0bb9fc1f62de353547aee03f`
- `scripts/zigux/check-phase1-bitmap-direct-anchors.py` at blob `0c1a206592e55ec9ca6f97ebd6fa097144f98b8d`
- `scripts/zigux/validate-phase1-closure.py` at blob `951d9c723759bb433a68eef2e682604c3f3e0d77`

## Survey Result

The current bitmap helper state reflects real Phase 1 progress, not repetitive wrapper churn. The helper body and its evidence packet keep review-visible coverage for:

- whole-word range edges and final partial-word clamping
- raw copy alias behavior, tail-clearing copy behavior, and copy-and-extend zero or aligned counts
- zero-sized destination-view no-op behavior and zero-bit logical short-circuit behavior
- exact-word-boundary equality masking and tail-masked predicates, weights, and weighted logical counts
- caller-window `xor` and `or` clamping, including multiword tail witnesses
- cross-word `bitmap_scnprintf()` range merging, truncation, terminator-only buffers, zero-length buffers, and empty-bitmap caller-buffer preservation
- Linux-style bitmap aliases for size, allocation, free/reset, mutation, predicates, and rendering

No helper-local code change was justified by this survey. The direct-anchor surfaces already match the roadmap and ledger-backed Phase 1 bitmap objective: the helper is present, bounded, reviewable, and guarded by exact marker checks plus the Phase 1 closure packet.

## Lane Rule

`tools/lib/bitmap.zig` stays parked unless a future repo-first reread finds one of these concrete conditions:

- direct-anchor drift in the bitmap helper tests or Linux-style alias surface
- committed shared replay drift in bitmap copy, logical, range, allocation, formatting, or partial-window parity fields
- mismatch between the helper, the Phase 1 helper manifest, the closure note, the lane-sequencing note, or `scripts/zigux/check-phase1-bitmap-direct-anchors.py`

Do not reopen older closure-side or missing-validator cue names by default, and do not batch bitmap follow-up with `find_bit`, `rbtree`, `string`, runtime bitmap, or later-phase ABI work in the same lane.
