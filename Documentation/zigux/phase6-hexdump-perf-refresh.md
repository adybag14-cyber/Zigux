# Phase 6 Hexdump Perf Refresh Evidence

This note preserves one bounded Phase 6 hexdump perf-gate finding so the `lib/hexdump` packet stays reviewable while the shared catalog, slice note, manifest, and harness thresholds are reconciled on a later safe pass.

## Scope

- roadmap family: `lib/hexdump.c` -> `lib/hexdump.zig`
- packet type: helper-local perf evidence only
- freeze-map posture: no runtime-core expansion, no helper semantic change, no workflow-policy widening

## Last Successful Focused Replay

The last attached-toolchain replay that cleanly exercised the shipped hexdump perf harness recorded these bounded results for the two committed formatter cases:

- `16B-plain`: `max_slowdown_pct = 175` remained sufficient, with the successful replay recording `slowdown_pct = 139`
- `32B-ascii-g2`: the grouped ASCII formatter replay needed a wider ceiling, with the successful replay recording `slowdown_pct = 518`

That replay kept the existing `fixtures.prepareExpectedLine(...)` reference path and did not change helper output semantics.

## Why This Matters

The Phase 6 roadmap requires perf gates for math-sensitive leaf helpers. The hexdump packet already ships a focused perf harness, but the grouped ASCII formatter path pays for both native-endian group formatting and the ASCII column. The preserved replay evidence shows why a case-local ceiling is the reviewable boundary instead of a single shared ceiling across both formatter cases.

## What This Note Does Not Claim

- this note does not claim that the shared Phase 6 catalog, hexdump slice note, manifest, or harness thresholds have already been updated on the same commit
- this note does not widen into helper logic, fixture shape, tests-root routing, Makefile policy, or broader perf governance
- this note does not replace the existing Phase 6 shared review surfaces; it preserves one bounded evidence point until those surfaces can be refreshed safely

## Next Bounded Step

When live repo file reads are reliable again, reconcile the existing shared Phase 6 hexdump surfaces to this preserved evidence by:

- keeping `16B-plain` at `max_slowdown_pct = 175`
- treating `32B-ascii-g2` as a separate grouped ASCII case with its own higher ceiling
- refreshing the coupled catalog, slice, manifest, and harness wording together on one bounded follow-up
