# Phase 6 Bsearch Slice

This document records the bounded Phase 6 leaf-helper validation slice for Zigux.

## Status

- `PHASE6_STATUS=active`
- `PHASE6_SLICE=bsearch-leaf-helper`
- scope: first low-risk binary-search helper coverage only
- lane posture: parked after the current parity surface cleared the bounded helper goal
- product boundary:
  - `lib/bsearch.zig`
  - `zigux/tests/phase6_bsearch.zig`
  - `zigux/tests/phase6_bsearch_perf.zig`
  - `zigux/tests/phase6_bsearch_c_parity.zig`
  - `zigux/tests/fixtures/phase6_bsearch_vectors.zig`
  - `zigux/tests/fixtures/phase6_bsearch_c_harness.c`
  - `scripts/zigux/check-phase6-bsearch-c-parity.py`
  - `zigux/tests/phase6_build.zig`
  - `zigux/Makefile`

## Why this slice exists

Phase 6 is where Zigux can keep proving low-risk in-kernel helper ports without stepping into runtime-core or driver complexity.

`lib/bsearch.c` is a good next slice because it is:

- leaf-oriented
- small enough to validate with deterministic sorted fixtures
- a clean API-parity target for comparator-driven helper behavior

## Gates

1. run the shared Phase 6 validator-first handoff before helper-local replay
- `python3 scripts/zigux/validate-phase6.py --self-test`
- `make -C zigux phase6-validate`

2. run the focused Zig Phase 6 helper tests
- `zig build test --build-file zigux/tests/phase6_build.zig`

3. keep the helper wired through the Zigux convenience target
- `make -C zigux phase6`

4. replay the bounded perf-sanity harness when reviewing lookup-cost drift
- `zig build bsearch-perf --build-file zigux/tests/phase6_build.zig`
- or `make -C zigux phase6-bsearch-perf`

5. replay the representative external C-vs-Zig parity spot check when portability-sensitive behavior is under review
- `python3 scripts/zigux/check-phase6-bsearch-c-parity.py`
- `python3 scripts/zigux/check-phase6-bsearch-c-parity.py --self-test`
- `zigux/tests/phase6_bsearch_c_parity.zig`
- `zigux/tests/fixtures/phase6_bsearch_c_harness.c`

## Current parity surface

The current bsearch helper surface exercised by this slice covers:

- `Comparator`
- `CComparator`
- `RawComparator`
- `CRawComparator`
- `bsearchIndex`
- `bsearch`
- `bsearchMutable`
- `searchIndex`
- `search`
- `searchMutable`

The current tests check:

- integer-key hits at the beginning, middle, and end of a sorted slice
- misses below, between, and above known values
- singleton and empty-slice lookups keep the same found-or-null boundary as the external parity replay
- heterogeneous-key lookup where the key type differs from the element type
- pointer-return parity for successful lookups
- mutable-pointer parity when searching mutable storage
- raw `bsearchIndex`, `bsearch`, and `bsearchMutable` parity for direct Linux-style callers, including mutable write-through behavior
- duplicate-key found-or-null parity without claiming stable selection across beginning, middle, and end duplicate runs
- runtime-selected comparator function pointers preserve the same found-or-null behavior across ascending and descending sorted slices
- runtime-selected C ABI comparator pointers preserve the same found-or-null behavior across ascending and descending sorted slices
- runtime-selected raw comparator pointers preserve the same found-or-null behavior across ascending and descending sorted slices
- runtime-selected C ABI raw comparator pointers preserve the same found-or-null behavior across ascending and descending sorted slices
- focused Zig Phase 6 tests now also prove runtime-selected descending typed and raw mutable-pointer write-through behavior instead of leaving that contract only to the external C-vs-Zig parity replay
- representative lookup work stays inside a bounded binary-search comparison budget on every replayed lookup, not only on average across the perf run
- inline sorted integer and symbol tables keep the current lookup-behavior corpus deterministic, while `zigux/tests/fixtures/phase6_bsearch_vectors.zig` now owns the perf case matrix plus the fixed edge, quarter, midpoint, final-hit, and paired miss probes that seed the shared perf replay
- a replayable perf-sanity harness reports lookup cost plus both average and worst-case comparator work for representative `256`-, `4096`-, and `65536`-entry sorted slices through the shared `zigux/tests/fixtures/phase6_bsearch_vectors.zig` corpus module while replaying the same deterministic edge, midpoint, seeded interior, and miss probes through typed and raw comparator paths for both ascending and descending order
- the external parity checker now also carries a built-in `--self-test` path for its missing-path guards, unexpected-extra-output guard, generated build template, and sorted-output normalization so reviewability does not depend only on a locally runnable `zig` plus `cc` pair
- a representative external C-vs-Zig parity replay currently replays 29 sorted lookup cases covering integer hits and misses, singleton and empty-slice behavior, ascending and descending comparator-driven lookups, direct raw-helper hit and miss behavior, raw descending lookup behavior, duplicate hits across beginning, middle, and end duplicate runs on a found-or-null basis without pinning a stable duplicate index, runtime-selected typed and raw comparator-pointer lookups across ascending and descending sorted slices for both hit and miss cases with distinct ascending-versus-descending miss labels, heterogeneous string-key lookup, and runtime-selected descending typed and raw mutable-pointer write-through behavior

## Non-goals

This slice does not yet claim:

- lower-bound or upper-bound helpers
- duplicate-key stability guarantees beyond matching the kernel-style found-or-null contract
- stable microbenchmark thresholds across machines

## Next bounded step

Leave the Phase 6 bsearch lane parked unless fresh repo inspection finds a concrete parity, perf, or directly coupled review-packet drift inside `lib/bsearch.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_bsearch_perf.zig`, `zigux/tests/phase6_bsearch_c_parity.zig`, `zigux/tests/fixtures/phase6_bsearch_vectors.zig`, `zigux/tests/fixtures/phase6_bsearch_c_harness.c`, `scripts/zigux/check-phase6-bsearch-c-parity.py`, or the shared Phase 6 packet.

Current shared Phase 6 surfaces already close the earlier note-only follow-up for this helper: `Documentation/zigux/phase6-helper-parity-catalog.md` now names the bsearch perf corpus fixture, the comparison-budget gate, and `PHASE6_BSEARCH_C_PARITY_CASES=29`, while `zigux/tests/phase6_helper_parity_manifest.json` records the same helper inventory and parity count. The next same-family follow-up should therefore stay narrow to refreshing those shared markers only if the shipped bsearch packet changes again, not to reopening this helper slice just to restate evidence that current `master` already records elsewhere.
