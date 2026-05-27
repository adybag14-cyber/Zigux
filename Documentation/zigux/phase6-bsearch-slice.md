# Phase 6 Bsearch Slice

## Status
- `PHASE6_STATUS=parked`
- `PHASE6_SLICE=bsearch-leaf-helper`
- lane state: helper slice restored; parked unless helper-local parity, portability, duplicate-span, raw C ABI bounds, fixture-backed perf replay, or compact fixture-companion drift reappears

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
- `IndexRange.sliceConst`
- `IndexRange.sliceMutable`
- `IndexRange.firstConst`
- `IndexRange.firstMutable`
- `IndexRange.lastConst`
- `IndexRange.lastMutable`
- `IndexRange.bytes`
- `IndexRange.bytesMutable`
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
- `zigux/tests/phase6_bsearch_perf.zig`
- `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`
- `zigux/tests/phase6_bsearch_c_abi_budget.zig`
- `zigux/tests/phase6_bsearch_c_parity.zig`
- `zigux/tests/fixtures/phase6_bsearch_c_harness.c`
- `zigux/tests/fixtures/phase6_bsearch_vectors.zig`
- direct helper-local evidence now covers typed and raw representative lookups, descending-order comparator handling, duplicate-span `equalRange` wrappers, `IndexRange` typed and byte-view companions, mutable write-through aliases, typed and raw C ABI lower-bound and upper-bound insertion-point parity, runtime-selected typed and raw C ABI comparator pointers under logarithmic comparison budgets, a representative external C-vs-Zig parity replay covering 17 sorted lookup cases across ascending and descending comparator-driven lookups, duplicate hits, heterogeneous string-key lookup, and mutable write-through behavior, and a fixture-backed dedicated perf replay that reports lookup cost plus average and worst-case comparator work across representative lengths
- the compact shared seed fixture companion keeps representative ascending, descending, duplicate, symbol, packed-record, deterministic query corpus, and dedicated perf-case lengths reviewable without widening this lane into speculative threshold recalibration or broader shared survey work
- helper-local checker: `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`
- shared perf-marker guard: `scripts/zigux/check-phase6-base64-bsearch-perf-markers.py`
- direct C parity checker: `scripts/zigux/check-phase6-bsearch-c-parity.py`
- shared helper-evidence row companion: `Documentation/zigux/phase6-helper-evidence-catalog.md`

## Current Bounded Next Step
If this helper reopens, keep the next move inside `lib/bsearch.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_bsearch_perf.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, `zigux/tests/phase6_bsearch_c_abi_budget.zig`, `zigux/tests/phase6_bsearch_c_parity.zig`, `zigux/tests/fixtures/phase6_bsearch_c_harness.c`, `zigux/tests/fixtures/phase6_bsearch_vectors.zig`, or this slice note only. The helper-local corpus checker `scripts/zigux/check-phase6-bsearch-corpus-evidence.py` now fail-closes the current corpus, duplicate-span, raw C ABI bounds, `IndexRange` helper-view companions, direct C parity replay, dedicated perf replay, shared helper-evidence catalog row, and build-route packet, while the shared perf-marker guard `scripts/zigux/check-phase6-base64-bsearch-perf-markers.py` keeps the machine-readable base64 and bsearch runtime diagnostics honest. The first safe follow-up after fresh repo inspection is rerunning `python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py`, `python3 scripts/zigux/check-phase6-base64-bsearch-perf-markers.py`, `python3 scripts/zigux/check-phase6-bsearch-c-parity.py`, `zig build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig`, and `zig build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig`, then keeping any repair to one helper-local parity, duplicate-span, `IndexRange` helper-view, perf-route, raw C ABI bound, fixture-companion, or note drift.
