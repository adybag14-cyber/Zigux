# Phase 9 Runtime Bitmap Sample Current Checks

Date: 2026-05-27

This note records the current sample-local verification for `samples/zigux/runtime_bitmap.zig`.

Repo-first reread on 2026-05-27 shows that `samples/zigux/runtime_bitmap.zig` is still part of the Phase 9 runtime pilot family, not one of the four approved Phase 5 reference samples. This note stays inside the existing runtime bitmap family and records the exact sample-local checks that current `master` exposes.

## Files reread

- `samples/zigux/runtime_bitmap.zig`
- `samples/zigux/runtime_bitmap_direct_init_contract.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `zigux/helpers/bitmap_view.zig`
- `zigux/tests/runtime_bitmap_survey.zig`

## Exact commands

- `zig fmt --check /workspace/.scratch/p5-l09/samples/zigux/runtime_bitmap.zig /workspace/.scratch/p5-l09/samples/zigux/runtime_bitmap_direct_init_contract.zig /workspace/.scratch/p5-l09/zigux/helpers/bitmap_view.zig`
- `cd /workspace/.scratch/p5-l09 && /workspace/.toolchains/p5-l09/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2/zig test --dep bitmap_view -Mroot=samples/zigux/runtime_bitmap.zig -Mbitmap_view=zigux/helpers/bitmap_view.zig`
- `cd /workspace/.scratch/p5-l09 && /workspace/.toolchains/p5-l09/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2/zig test --dep runtime_bitmap_sample -Mroot=samples/zigux/runtime_bitmap_direct_init_contract.zig --dep bitmap_view -Mruntime_bitmap_sample=samples/zigux/runtime_bitmap.zig -Mbitmap_view=zigux/helpers/bitmap_view.zig`

## Checked behavior on current master

1. Review contract and anchor.
   - descriptor name is `runtime_bitmap`
   - anchor is `lib/test_bitmap.c`
   - review focus keeps `descriptor_and_anchor`, `summary_replay`, `sparse_iteration`, `parse_and_print`, `range_mutation_and_copy`, `selftest_lifecycle`, `exit_lifecycle_and_guards`, and `top_bit_contract` explicit

2. Sparse-summary replay.
   - direct init with `{ 10, 20, 30, 40, 50, 60, 80, 123 }` yields `first_set = 10`, `first_zero = 0`, `weight = 8`, `nthSetBit(0) = 10`, `nthSetBit(7) = 123`, `nthSetBit(8) = null`, and `countSetBitsInRange(0, 81) = 7`

3. Parse, print, and range-mutation replay.
   - parsed bit list `0, 5, 64, 70` formats back to `0,5,64,70`
   - after `clearRange(word_bits, 2)` and `setRange(9, 4)`, the sample keeps `first_set = 0`, `first_zero = 1`, `weight = 7`, bit `12` set, bit `word_bits + 6` set, bit `word_bits` clear, and `countSetBitsInRange(9, 4) = 4`

4. Non-destructive range guards.
   - `setRange(bitmap_nbits, 0)` and `clearRange(bitmap_nbits, 0)` leave the sample unchanged
   - `setRange(bitmap_nbits, 1)` and `clearRange(bitmap_nbits - 1, 2)` both return `error.BitRangeOutOfBounds` without mutating the sample

5. Parsed-list normalization and empty input.
   - duplicate parsed lists collapse to the same four-bit summary and format string `0,5,64,70`
   - a whitespace-only bit list initializes an empty bitmap with `first_set = bitmap_nbits`, `first_zero = 0`, and `weight = 0`, and that empty state remains stable through direct exit

6. Rejected parsed init stays cold.
   - `0,,64` returns `error.InvalidBitList`
   - a parsed list containing `bitmap_nbits` returns `error.BitRangeOutOfBounds`
   - both rejected inputs keep the sample cold, empty, and at zero init/selftest/exit counts

7. Selftest, copy, and exit lifecycle.
   - selftest returns anchor `lib/test_bitmap.c`, four operation families, `checked_range_mutations = true`, and `checked_iteration_paths = true`
   - `copyFrom(...)` accepts initialized and selftest-complete sources, but rejects cold and exited sources with `error.InvalidSourceLifecycle`
   - `exit()` blocks later mutation, selftest replay, and re-exit with `error.InvalidLifecycleTransition`

8. Summary-stability guards.
   - re-selftest, re-init from initialized state, re-init from selftest-complete state, direct exit without selftest, and re-init after exit all preserve the expected counters and bit state
   - out-of-range direct init arrays keep the sample cold and empty

9. Direct-init companion checks.
   - unsorted duplicate direct-init bits `{ 70, 5, 0, 64, 70, 5 }` collapse to the same four-bit sparse summary and formatted output `0,5,64,70`
   - `countSetBitsInRange(64, 7) = 2`
   - selftest plus exit keep the direct-init bitmap shape stable while only the lifecycle counters advance

## Exact validation results

- `runtime_bitmap.zig`: `All 15 tests passed.`
- `runtime_bitmap_direct_init_contract.zig`: `All 2 tests passed.`

## Boundaries

This note records current sample-local behavior only.

It does not claim:

- loadable Phase 9 runtime bitmap pilot-module parity
- broader shared runtime-loader parity
- any Phase 5 reference-sample status for the runtime bitmap family
