# Phase 6 Bsearch Slice

This document starts a bounded Phase 6 leaf-helper validation slice for Zigux.

## Status

- `PHASE6_STATUS=active`
- `PHASE6_SLICE=bsearch-leaf-helper`
- scope: first low-risk binary-search helper coverage only
- product boundary:
  - `lib/bsearch.zig`
  - `zigux/tests/phase6_bsearch.zig`
  - `zigux/tests/phase6_build.zig`
  - `zigux/Makefile`

## Why this slice exists

Phase 6 is where Zigux can keep proving low-risk in-kernel helper ports without stepping into runtime-core or driver complexity.

`lib/bsearch.c` is a good next slice because it is:

- leaf-oriented
- small enough to validate with deterministic sorted fixtures
- a clean API-parity target for comparator-driven helper behavior

## Gates

1. run the focused Zig Phase 6 helper tests
- `zig build test --build-file zigux/tests/phase6_build.zig`

2. keep the helper wired through the Zigux convenience target
- `make -C zigux phase6`

3. replay the bounded perf-sanity harness when reviewing lookup-cost drift
- `make -C zigux phase6-bsearch-perf`

4. replay the representative external C-vs-Zig parity spot check when portability-sensitive behavior is under review
- `python3 scripts/zigux/check-phase6-bsearch-c-parity.py`

## Current parity surface

The current bsearch helper surface exercised by this slice covers:

- `searchIndex`
- `search`
- `searchMutable`

The current tests check:

- integer-key hits at the beginning, middle, and end of a sorted slice
- misses below, between, and above known values
- heterogeneous-key lookup where the key type differs from the element type
- pointer-return parity for successful lookups
- mutable-pointer parity when searching mutable storage
- duplicate-key found-or-null parity without claiming stable duplicate selection
- representative lookup work stays inside a bounded binary-search comparison budget
- a replayable perf-sanity harness reports lookup cost and average comparator work for representative sorted slices
- a representative external C-vs-Zig parity replay covers integer hits and misses, singleton and empty-slice behavior, duplicate hits, heterogeneous string-key lookup, and mutable-pointer write-through behavior

## Non-goals

This slice does not yet claim:

- lower-bound or upper-bound helpers
- duplicate-key stability guarantees beyond matching the kernel-style found-or-null contract
- stable microbenchmark thresholds across machines

## Next bounded step

Leave the Phase 6 bsearch lane parked unless fresh repo inspection shows a concrete regression in the helper, its Zig parity tests, the bounded perf-sanity harness, or the representative external C-vs-Zig parity replay. There is no richer upstream `bsearch` fixture family to port right now, so the next honest follow-up would be a newly observed drift rather than speculative fixture growth.
