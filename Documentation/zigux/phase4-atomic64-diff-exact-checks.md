# Phase 4 Atomic64 Diff Exact Checks

This note records the exact bounded checks visible on `master` as of 2026-05-08 for the roadmap target `zigux/tests/atomic64_diff.zig`.

## Scope

- lane: `P4-L03`
- phase: `Phase 4`
- roadmap target: `zigux/tests/atomic64_diff.zig`
- wrapper blob: `873721b47f378ec6e7b3e46d2a7a0388e8dac8e7`
- runtime replay blob: `d3c082339d3357d7f4ed458313966705a7a9c409`
- manifest blob: `225fe4ef35ba0a76c8dc1fe45912b3e8d8bc78cc`
- shared validator blob: `602b1ff6ee9baf2874a3456704b250ae1086ee87`
- validation matrix blob: `5c680042a517d35c053a12df794676822d710ea3`

## Exact Bounded Checks

1. Arithmetic sequencing is explicit for two cases: the canonical `0x2aaa_3137_4001_500d` seed and the `-1` add or subtract path. The replay checks `addCounter`, `subCounter`, `addReturnCounter`, `subReturnCounter`, `incReturnCounter`, and `decReturnCounter` against exact expected values.
2. Exchange coverage is explicit for three cases: `v0 -> v1`, `v1 -> v2`, and a `std.math.minInt(i64)` high-bit starter that round-trips through exchange and restore.
3. Compare-and-swap coverage is explicit for both bounded outcomes: one success case that stores the desired value and one mismatch case that preserves the original value and reports `stored = false`.
4. `add_unless` coverage is explicit for both bounded outcomes: one blocked case that leaves the counter untouched and one changed case that applies the addend and reports `changed = true`.
5. Bitwise coverage is explicit for three bounded operations: `and`, `or`, and `xor`, each with exact starter, mask, previous-value, and final-value expectations.
6. Selftest-family coverage is explicit through `runSelftest()`: the replay checks the Linux anchor string `lib/atomic64_test.c`, requires five operation families in order, requires the returning, bitwise, and guard flags, and checks that post-exit mutating calls fail with `error.InvalidLifecycleTransition`.
7. Threshold-replay coverage is explicit but still correctness-only: the gate rejects `runThresholdReplay(0)`, exact-pins the `1`-iteration and `4`-iteration summaries, checks `final_stage`, `final_selftest_runs`, `final_exit_runs`, `final_counter`, and `checksum`, and requires that the `4`-iteration replay is deterministic across repeated runs while still differing from the `1`-iteration checksum.

## Current Replay Routes

- shared validator route: `python3 scripts/zigux/validate-phase4.py`
- shared Zig replay route: `zig build test --build-file zigux/tests/phase4_build.zig`
- local atomic64 route: `zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig`

## Current Posture

The current gate is broader than a simple exchange-only wrapper, but it is still a bounded correctness gate. The live `Documentation/zigux/phase4-validation-matrix.md` posture remains correct: there is still no approved hard timing threshold for this lane, and the next truthful expansion would be one bounded benchmark command plus one acceptable limit rather than widening the semantic surface first.
