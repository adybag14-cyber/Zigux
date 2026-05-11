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

Fresh repo-first inspection shows that the older saved bitmap closure-validator blocker is already closed on current `master`.

The Phase 1 closure validator already carries the bitmap final-partial-word and Linux-style alias closure markers that older lane memory still described as missing. Future runs should not reopen that already-landed validator sync.

The older saved `scripts/zigux/validate-phase1.py` write-text handoff is already closed on current `master` as well. The built-in Phase 1 validator self-test now uses `Path.write_text()`, so future runs should not replay that typo-only repair or keep treating it as the next same-lane deliverable.

The docs-root Phase 1 summary still names this owner-map note, so the earlier `Documentation/zigux/README.md` truthfulness gap remains closed on current `master`.

Fresh bench-packet rereads now show that the next smallest same-lane gap is the unlanded `find_bit` edge bench widening instead: current `zigux/tests/phase1_bench.zig` still stops short of the underscore alias and backward-edge `findLastBit()` replay paths that live `tools/lib/find_bit.zig` already keeps review-visible, and `zigux/tests/fixtures/phase1_bench_expectations.json` still pins the older exact edge checksum `12820000`.

The closed PR history for `test(zigux): tighten Phase 1 find_bit edge bench gate` still matches that live gap. Recomputing the widened edge packet against current `tools/lib/find_bit.zig` behavior yields a per-iteration checksum of `1167`, so the exact Phase 1 edge-bench contract should become `23340000` at `20000` iterations when the underscore alias and tail-edge last-bit calls land beside the existing boundary, tail-clamp, and past-`nbits` probes.

## Anti-Overlap Rules

When this lane reopens, stay inside one bounded step only.

- Do not batch shared-replay parked helpers with the direct-anchor helper family.
- Do not reopen the already-landed bitmap closure-marker repair.
- Do not reopen the already-landed `validate-phase1.py` write-text typo repair.
- Do not reopen the already-landed docs-root owner-map sync.
- Prefer the smallest same-family reviewability, parity-gate, fixture, benchmark, or build-route repair before changing helper semantics.
- If the exact direct-anchor gap is already closed on `master`, advance only to the next unfinished bounded step inside the same helper family.

## Next Bounded Step

The next honest same-lane follow-up is to land the two-file `find_bit` edge bench-gate sync in:

- `zigux/tests/phase1_bench.zig`
- `zigux/tests/fixtures/phase1_bench_expectations.json`

That bounded change should add the underscore alias and backward-edge `findLastBit()` replay calls to `findBitEdgeBench()`, then refresh `PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM` from `12820000` to `23340000` without widening into helper semantics or broader Phase 1 surface churn.

Until that bench-gate sync lands, keep Phase 1 follow-up work parked on review-surface truthfulness, closure accuracy, fixture drift, benchmark exactness, or other already-shipped parity-gate surfaces rather than reopening helper behavior.

## Footer

This note is lane-local coordination only. It does not reopen the closed Phase 1 helper tranche or imply wider product scope.
