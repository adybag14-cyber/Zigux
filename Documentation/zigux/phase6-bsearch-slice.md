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
- `bsearchIndex`
- `bsearch`
- `bsearchMutable`
- `bsearchLowerBoundIndex`
- `bsearchUpperBoundIndex`

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

## Current Bounded Next Step
If this helper reopens, first rerun `python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py` and `zig build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig` against current `master`, then keep the follow-up inside one packet-local surface only: `Documentation/zigux/phase6-bsearch-slice.md`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, `zigux/tests/phase6_bsearch_c_abi_budget.zig`, or `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`. Do not widen the reopen step into shared Phase 6 routing, a separate fixture module, or a standalone timing-style perf target unless the current bsearch packet itself actually drifts.
