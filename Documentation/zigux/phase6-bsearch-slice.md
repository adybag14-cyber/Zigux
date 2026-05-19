# Phase 6 Bsearch Slice

## Status
- `PHASE6_STATUS=parked`
- `PHASE6_SLICE=bsearch-leaf-helper`
- lane state: helper slice restored; parked unless helper-local parity, portability, duplicate-span, raw C ABI bounds, or compact fixture-companion drift reappears

## API Surface
- `searchIndex`
- `search`
- `searchMutable`
- `lowerBoundIndex`
- `lowerBound`
- `lowerBoundMutable`
- `upperBoundIndex`
- `upperBound`
- `upperBoundMutable`
- `IndexRange`
- `equalRangeIndex`
- `equalRange`
- `equalRangeMutable`
- `bsearchIndex`
- `bsearch`
- `bsearchMutable`
- `bsearchLowerBoundIndex`
- `bsearchLowerBound`
- `bsearchLowerBoundMutable`
- `bsearchUpperBoundIndex`
- `bsearchUpperBound`
- `bsearchUpperBoundMutable`
- `bsearchEqualRangeIndex`
- `bsearchEqualRange`
- `bsearchEqualRangeMutable`

## Review Surface
- `lib/bsearch.zig`
- `zigux/tests/phase6_bsearch.zig`
- `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`
- `zigux/tests/phase6_bsearch_c_abi_budget.zig`
- `zigux/tests/fixtures/phase6_bsearch_vectors.zig`
- direct helper-local evidence now covers typed and raw representative lookups, descending-order comparator handling, duplicate-span `equalRange` wrappers, mutable write-through aliases, raw C ABI lower-bound and upper-bound insertion-point parity, and runtime-selected raw C ABI comparator pointers under logarithmic comparison budgets
- the compact shared seed fixture companion keeps representative ascending, descending, duplicate, symbol, packed-record, and deterministic query corpus reviewable without widening this lane into a standalone timing route
- helper-local checker: `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`
- shared helper-evidence row companion: `Documentation/zigux/phase6-helper-evidence-catalog.md`

## Current Bounded Next Step
If this helper reopens, keep the next move inside `lib/bsearch.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, `zigux/tests/phase6_bsearch_c_abi_budget.zig`, `zigux/tests/fixtures/phase6_bsearch_vectors.zig`, or this slice note only. The helper-local corpus checker `scripts/zigux/check-phase6-bsearch-corpus-evidence.py` now fail-closes the current corpus, duplicate-span, raw C ABI bounds, shared helper-evidence catalog row, and build-route packet, so the first safe follow-up after fresh repo inspection is rerunning `python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py` and `zig build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig`, then keeping any repair to one helper-local parity, duplicate-span, raw C ABI bound, fixture-companion, or note drift.
