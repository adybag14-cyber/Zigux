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

## Current Bounded Next Step
If this helper reopens, keep the next move inside `lib/bsearch.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, `zigux/tests/phase6_bsearch_c_abi_budget.zig`, `zigux/tests/fixtures/phase6_bsearch_vectors.zig`, or this slice note only. The first safe follow-up after fresh repo inspection is rerunning `zig build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig`, then keeping any repair to one helper-local parity, duplicate-span, raw C ABI bound, fixture-companion, or note drift inside the already-materialized packet. No dedicated `bsearch` corpus-checker file is currently materialized on `master`, so this lane should not treat one as a required reopen prerequisite.