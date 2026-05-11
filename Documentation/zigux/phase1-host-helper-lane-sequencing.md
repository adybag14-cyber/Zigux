# Phase 1 Host-Helper Lane Sequencing

This note keeps the closed Phase 1 host-helper packet reviewable without reopening helper semantics or batching unrelated follow-up work back together.

## Scope

Phase 1 stays limited to the roadmap-backed host-side helper tranche:

- `tools/lib/bitmap.zig`
- `tools/lib/find_bit.zig`
- `tools/lib/string.zig`
- `tools/lib/rbtree.zig`
- tightly coupled parity, closure, benchmark, and review-surface gates that already belong to that helper packet

Do not use this lane to widen into runtime helpers, Phase 3 ABI work, sample work, or later driver phases.

## Current Split

The live Phase 1 packet on `master` is already closed as a bounded helper tranche, but it is intentionally split into two follow-up families.

### Shared-Replay Parked Helpers

These helpers reopen only for shared replay drift, fixture drift, build-route drift, or review-surface truthfulness:

- `tools/lib/argv_split.zig`
- `tools/lib/cmdline.zig`
- `tools/lib/ctype.zig`
- `tools/lib/hweight.zig`
- `tools/lib/list_sort.zig`
- `tools/lib/slab.zig`
- `tools/lib/str_error_r.zig`
- `tools/lib/vsprintf.zig`
- `tools/lib/zalloc.zig`

### Direct-Anchor Follow-Up Helpers

These are the only helpers that still keep bounded direct helper-local follow-up anchors on current `master`:

- `tools/lib/bitmap.zig`
- `tools/lib/find_bit.zig`
- `tools/lib/rbtree.zig`
- `tools/lib/string.zig`

## Current Repo Reality

Fresh repo-first inspection shows the older saved Phase 1 reopen cues are already closed on current `master`.

The Phase 1 closure validator already carries the bitmap final-partial-word and Linux-style alias closure markers that older lane memory once described as missing. Future runs should not reopen that already-landed validator sync.

The older saved `scripts/zigux/validate-phase1.py` write-text handoff is already closed on current `master` as well. The built-in Phase 1 validator self-test now uses `Path.write_text()`, so future runs should not replay that typo-only repair or keep treating it as the next same-lane deliverable.

The docs-root Phase 1 summary still names this owner-map note, so the earlier `Documentation/zigux/README.md` truthfulness gap remains closed on current `master`.

The earlier `find_bit` edge bench gap is now closed on current `master` too. `zigux/tests/phase1_bench.zig` now carries the underscore-alias and backward-edge `findLastBit()` replay calls inside `findBitEdgeBench()`, and `zigux/tests/fixtures/phase1_bench_expectations.json` already keeps the widened exact edge checksum at `23340000`.

The earlier shared closure-note gap is closed on current `master` too. `Documentation/zigux/phase1-closure.md` already keeps `Documentation/zigux/phase1-host-helper-lane-sequencing.md` inside its shared review packet, matching the docs root, scripts root, tests root, and review checklist reminder surfaces.

That means the next honest same-lane follow-up is no longer another saved validator patch, bench-body repair, or closure-note reminder sync. Fresh repo-first inspection now points at the shared Phase 1 validator packet instead: the next bounded same-lane step is the smallest exact-check drift still visible around the live `find_bit` review-anchor packet in `scripts/zigux/validate-phase1.py`, not another helper-semantics change.

Future host-tools follow-up should come only from the next freshly observed same-packet truthfulness or exact-check drift across the shipped Phase 1 closure, manifest, validator, benchmark, or helper-local anchor surfaces.

## Anti-Overlap Rules

When this lane reopens, stay inside one bounded step only.

- Do not batch shared-replay parked helpers with the direct-anchor helper family.
- Do not reopen the already-landed bitmap closure-marker repair.
- Do not reopen the already-landed `validate-phase1.py` write-text typo repair.
- Do not reopen the already-landed docs-root owner-map sync.
- Do not reopen the already-landed `find_bit` edge bench sync.
- Do not reopen the already-landed shared closure-note owner-map sync.
- Prefer the smallest same-family reviewability, parity-gate, fixture, benchmark, or build-route repair before changing helper semantics.
- If the exact direct-anchor gap is already closed on `master`, advance only to the next unfinished bounded step inside the same helper family.

## Next Bounded Step

Leave this lane parked unless fresh repo-first inspection finds another equally small same-lane truthfulness or exact-check gap inside one already-landed Phase 1 surface such as:

- `Documentation/zigux/phase1-closure.md`
- `zigux/tests/fixtures/phase1_helper_manifest.json`
- `scripts/zigux/validate-phase1.py`
- `scripts/zigux/validate-phase1-closure.py`
- `zigux/tests/phase1_bench.zig`
- one existing direct helper-local anchor in `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, or `tools/lib/string.zig`

Until a new concrete gap appears, keep Phase 1 follow-up work parked on review-surface truthfulness, closure accuracy, fixture drift, benchmark exactness, or other already-shipped parity-gate surfaces rather than reopening helper behavior.

## Footer

This note is lane-local coordination only. It does not reopen the closed Phase 1 helper tranche or imply wider product scope.
