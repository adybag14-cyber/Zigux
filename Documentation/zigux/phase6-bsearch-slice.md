# Phase 6 Bsearch Slice

## Status
- `PHASE6_STATUS=parked`
- `PHASE6_SLICE=bsearch-leaf-helper`
- lane state: helper slice landed; parked unless a new `bsearch.c` parity, comparison-budget, lower- or upper-bound companion, or packet-alignment drift appears

## API Surface
- `searchIndex`
- `search`
- `searchMutable`
- `bsearchIndex`
- `bsearch`
- `bsearchMutable`

## Review Surface
- `lib/bsearch.zig`
- `zigux/tests/phase6_bsearch.zig`
- `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`
- `zigux/tests/phase6_bsearch_c_abi_budget.zig`
- `zigux/tests/fixtures/phase6_bsearch_vectors.zig`
- direct local rerun route: `zig build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig`
- Linux-style rerun route: `make -C zigux phase6-bsearch-test`
- `python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py --self-test`
- focused typed and raw lower- and upper-bound C ABI parity across ascending and descending sorted inputs plus packed-record `member_size` boundaries through `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`
- focused direct C ABI equality-budget parity across typed and raw ascending and descending sorted inputs plus packed-record `member_size` ranges through `zigux/tests/phase6_bsearch_c_abi_budget.zig`
- runtime-selected raw C ABI comparator pointer parity, including descending-order lookup, pointer-return duplicate hits, mutable write-through, and null misses

The current packet intentionally keeps its representative sorted inputs inline in `zigux/tests/phase6_bsearch.zig` so the helper bundle stays small and directly reviewable, while `zigux/tests/fixtures/phase6_bsearch_vectors.zig` carries the bounded deterministic query-seeding and case-size corpus shared by the focused bsearch replays. The same packet still keeps its bounded comparison-budget evidence instead of a dedicated `phase6_bsearch_perf` route, and the dedicated bsearch-only rerun routes keep that packet reviewable without dragging the rest of the shared Phase 6 helper bundle into every follow-up.
