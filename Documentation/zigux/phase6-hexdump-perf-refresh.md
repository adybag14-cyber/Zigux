# Phase 6 Hexdump Perf Refresh Evidence

This note preserves one bounded Phase 6 hexdump perf-gate finding so the `lib/hexdump` packet stays reviewable alongside the now-aligned shared catalog, slice note, manifest, and harness thresholds on `master`.

## Scope

- roadmap family: `lib/hexdump.c` -> `lib/hexdump.zig`
- packet type: helper-local perf evidence only
- owner lane: `P6-Y09`
- review-surface owner: this preserved replay note stays helper-local to the `lib/hexdump.zig` packet and must remain aligned with `Documentation/zigux/phase6-hexdump-slice.md` plus `scripts/zigux/check-phase6-hexdump-packet.py`, not a shared Phase 6 perf-governance lane
- freeze-map posture: no runtime-core expansion, no helper semantic change, no workflow-policy widening

## Last Successful Focused Replay

The last attached-toolchain replay that cleanly exercised the shipped hexdump perf harness recorded these bounded results for the two committed formatter cases that motivated the current grouped-output ceilings:

- `16B-plain`: `max_slowdown_pct = 175` remained sufficient, with the successful replay recording `slowdown_pct = 139`
- `32B-ascii-g2`: the grouped ASCII formatter replay needed a wider ceiling, with the successful replay recording `slowdown_pct = 518`

That replay kept the existing `fixtures.prepareExpectedLine(...)` reference path and did not change helper output semantics.

## Current Master Alignment

Current `master` now carries the reconciled shared Phase 6 hexdump perf packet beside this preserved replay note:

- `Documentation/zigux/phase6-perf-gate-survey.md` records the shipped four-case hexdump threshold matrix
- `zigux/tests/phase6_helper_parity_manifest.json` records the same helper-local hexdump replay and threshold cases
- `zigux/tests/fixtures/phase6_hexdump_vectors.zig` carries the live `16B-plain-g1`, `32B-ascii-g2`, `16B-ascii-g4`, and `16B-ascii-g8` perf rows

This note now serves as the bounded rationale for why the grouped ASCII formatter case keeps a higher ceiling than the plain formatter case, not as a placeholder for a still-unlanded threshold refresh.

## Why This Matters

The Phase 6 roadmap requires perf gates for math-sensitive leaf helpers. The hexdump packet already ships a focused perf harness, but the grouped ASCII formatter path pays for both native-endian group formatting and the ASCII column. The preserved replay evidence shows why a case-local ceiling is the reviewable boundary instead of a single shared ceiling across both formatter cases.

## What This Note Does Not Claim

- this note does not widen into helper logic, fixture shape, tests-root routing, Makefile policy, or broader perf governance
- this note does not replace the shared Phase 6 catalog, slice, manifest, or harness thresholds; it complements them with one preserved focused replay result
- this note does not claim that every grouped ASCII width shares the exact same slowdown profile; it only preserves the focused evidence that justified separating the grouped formatter ceiling from the plain formatter ceiling

## Next Bounded Step

If the Phase 6 hexdump packet reopens, rerun the focused attached-toolchain replay and confirm that the preserved `16B-plain` and `32B-ascii-g2` evidence still matches the live shared Phase 6 threshold surfaces before widening into any helper-semantic work.
