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
- direct local rerun route: `zig build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig`
- Linux-style rerun route: `make -C zigux phase6-bsearch-test`
- direct local corpus evidence checker route: `python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py`
- direct local corpus evidence checker self-test: `python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py --self-test`
- focused typed and raw lower- and upper-bound C ABI parity across ascending and descending sorted inputs plus packed-record `member_size` boundaries through `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`
- focused direct C ABI equality-budget parity across typed and raw ascending and descending sorted inputs plus packed-record `member_size` ranges through `zigux/tests/phase6_bsearch_c_abi_budget.zig`
- runtime-selected raw C ABI comparator pointer parity, including descending-order lookup, pointer-return duplicate hits, mutable write-through, and null misses

The current packet intentionally keeps its representative sorted inputs, deterministic query seeding, and case-size corpus inline in the focused `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, and `zigux/tests/phase6_bsearch_c_abi_budget.zig` replays so the helper bundle stays small and directly reviewable without a separate `phase6_bsearch_vectors` fixture module. The same packet still keeps its bounded comparison-budget evidence instead of a dedicated `phase6_bsearch_perf` route, and the dedicated bsearch-only rerun routes keep that packet reviewable without dragging the rest of the shared Phase 6 helper bundle into every follow-up.

Current `master` still carries `zigux/tests/fixtures/phase6_bsearch_vectors.zig`, but only as a parked seed companion that mirrors the representative ascending, descending, hit-or-miss, symbol, and packed-record cases already exercised inline. Reviewers should treat that file as support evidence outside the executable packet rather than as a separate replay surface or a standalone timing-style perf route.

Current public-tree correction: direct current-`master` reads for this helper now show `lib/bsearch.zig`, this slice note, `zigux/tests/fixtures/phase6_bsearch_vectors.zig`, and `zigux/tests/phase6_helper_parity_manifest.json`, but do not currently expose `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, or `zigux/tests/phase6_bsearch_c_abi_budget.zig`. Treat those three replay paths as missing current-master evidence until a helper-local follow-up restores them; until then, the checker and rerun routes above are the intended closure surface rather than presently runnable proof.

## Current Bounded Next Step
If this helper reopens, first do one helper-local closure step only: either restore `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, and `zigux/tests/phase6_bsearch_c_abi_budget.zig` and then rerun `python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py` plus `zig build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig`, or rewrite only the bsearch-local note and checker surfaces so they no longer advertise those three replays as current-`master` evidence. Do not widen the reopen step into shared Phase 6 routing, a separate fixture module, or a standalone timing-style perf target unless the current bsearch packet itself actually drifts.
