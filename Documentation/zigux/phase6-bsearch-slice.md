# Phase 6 Bsearch Slice

## Status
- `PHASE6_STATUS=parked`
- `PHASE6_SLICE=bsearch-leaf-helper`
- lane state: helper slice restored; parked unless helper-local parity, portability, duplicate-span, or compact fixture-companion drift reappears

## API Surface
- `searchIndex`
- `search`
- `searchMutable`
- `lowerBoundIndex`
- `upperBoundIndex`
- `IndexRange`
- `equalRangeIndex`
- `equalRange`
- `equalRangeMutable`
- `bsearchIndex`
- `bsearch`
- `bsearchMutable`
- `bsearchLowerBoundIndex`
- `bsearchUpperBoundIndex`
- `bsearchEqualRangeIndex`
- `bsearchEqualRange`
- `bsearchEqualRangeMutable`

## Review Surface
- `lib/bsearch.zig`
- `zigux/tests/phase6_bsearch.zig`
- `zigux/tests/fixtures/phase6_bsearch_vectors.zig`
- direct helper-local evidence now covers typed and raw representative lookups, descending-order comparator handling, duplicate-span `equalRange` wrappers, mutable write-through aliases, and runtime-selected raw C ABI comparator pointers
- the compact shared seed fixture companion keeps representative ascending, descending, duplicate, symbol, packed-record, and deterministic query corpus reviewable without widening this lane into a standalone timing route

## Current Bounded Next Step
If this helper reopens, keep the next move inside `lib/bsearch.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/fixtures/phase6_bsearch_vectors.zig`, or this slice note only. The first safe follow-up after this restore would be re-materializing the bounds-focused C ABI replay companions or the dedicated corpus checker if current master needs them again, not broadening helper semantics.