# Phase 6 Bsearch Slice

## Status
- `PHASE6_STATUS=parked`
- `PHASE6_SLICE=bsearch-leaf-helper`
- lane state: helper slice landed; parked unless a new `bsearch.c` parity, comparison-budget, lower- or upper-bound companion, or packet-alignment drift appears

## API Surface
- `searchIndex`
- `search`
- `searchMutable`
- `lowerBoundIndex`
- `upperBoundIndex`
- `IndexRange`
- `equalRangeIndex`
- `bsearchIndex`
- `bsearch`
- `bsearchMutable`
- `bsearchLowerBoundIndex`
- `bsearchUpperBoundIndex`
- `bsearchEqualRangeIndex`

## Review Surface
- `lib/bsearch.zig`
- `zigux/tests/phase6_bsearch.zig`
- `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`
- `zigux/tests/phase6_bsearch_c_abi_budget.zig`
- compact shared seed fixture companion: `zigux/tests/fixtures/phase6_bsearch_vectors.zig`
- direct local rerun route: `zig build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig`
- Linux-style rerun route: `make -C zigux phase6-bsearch-test`
- direct local corpus evidence checker route: `python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py`
- direct local corpus evidence checker self-test: `python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py --self-test`
- focused typed and raw lower- and upper-bound C ABI parity across ascending and descending sorted inputs plus packed-record `member_size` boundaries through `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`
- focused direct C ABI equality-budget parity across typed and raw ascending and descending sorted inputs plus packed-record `member_size` ranges through `zigux/tests/phase6_bsearch_c_abi_budget.zig`
- runtime-selected raw C ABI comparator pointer parity, including descending-order lookup, pointer-return duplicate hits, mutable write-through, and null misses

The current packet intentionally keeps the direct equality probes, duplicate-span checks, descending-order paths, and mutable write-through coverage concentrated in `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, and `zigux/tests/phase6_bsearch_c_abi_budget.zig` so the helper surface stays small and directly reviewable. The shared `zigux/tests/fixtures/phase6_bsearch_vectors.zig` companion is still part of that executable packet today: `phase6_bsearch.zig` reuses its representative ascending and descending arrays, and the bounds-focused plus direct C ABI budget replays reuse its dynamic-length and packed-record seed corpus.

Reviewers should treat that fixture as compact shared packet support rather than as a separate standalone timing-style route.

Within that helper-local surface, the exported `IndexRange` result type keeps duplicate-span length, emptiness, typed slice, and raw byte views explicit through `len`, `isEmpty`, `sliceConst`, `sliceMutable`, `bytes`, and `bytesMutable` without widening Phase 6 into a separate wrapper family.

## Current Bounded Next Step
If this helper reopens, first rerun `python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py` plus `zig build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig`, then keep the next repair inside one helper-local surface only. Do not widen the reopen step into shared Phase 6 routing, a separate fixture module, or a standalone timing-style perf target unless the current bsearch packet itself actually drifts.
