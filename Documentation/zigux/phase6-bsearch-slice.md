# Phase 6 Bsearch Slice

This document starts a bounded Phase 6 leaf-helper validation slice for Zigux.

## Status

- `PHASE6_STATUS=parked`
- `PHASE6_SLICE=bsearch-leaf-helper`
- scope: parked helper-local bsearch parity and comparison-budget packet only
- lane state: helper slice landed; parked unless a new `bsearch.c` parity, comparison-budget, or packet-alignment drift appears
- product boundary:
  - `lib/bsearch.zig`
  - `zigux/tests/phase6_bsearch.zig`
  - `zigux/tests/phase6_build.zig`
  - `zigux/Makefile`
- evidence note: direct readback on `2026-05-07` inspected the current `lib/bsearch.c`, `lib/bsearch.zig`, and `zigux/tests/phase6_bsearch.zig` packet so this slice stays limited to the shipped helper-local review surface instead of stale blob bookkeeping

## Why this slice exists

Phase 6 is where Zigux can keep proving low-risk in-kernel helper ports without stepping into runtime-core or driver complexity.

`lib/bsearch.c` is a good next slice because it is:

- leaf-oriented
- small enough to validate with deterministic sorted inputs kept directly in the focused replay
- a clean API-parity target for comparator-driven helper behavior

## Gates

1. run the focused Zig Phase 6 helper tests
- `zig build test --build-file zigux/tests/phase6_build.zig`

2. keep the helper wired through the Zigux convenience target
- `make -C zigux phase6`

3. keep the helper-local comparison-budget replay aligned with the current helper packet
- `zigux/tests/phase6_bsearch.zig`

4. keep the shared Phase 6 surface checker aligned with this slice
- `make -C zigux phase6-validate`

## Current parity surface

The current bsearch helper surface exercised by this slice covers:

- `searchIndex`
- `search`
- `searchMutable`
- `bsearchIndex`
- `bsearch`
- `bsearchMutable`
- `Comparator`
- `CComparator`
- `RawComparator`
- `CRawComparator`

The current tests check:

- integer-key hits at the beginning, middle, and end of a sorted slice
- misses below, between, and above known values
- comparator-driven descending-order lookup without widening the helper surface
- heterogeneous-key lookup where the key type differs from the element type
- pointer-return parity for successful typed lookups
- mutable typed and raw lookup write-through parity
- duplicate-key found-or-null parity without claiming stable duplicate selection
- raw empty-input parity, including that the comparator is not invoked when `num_members == 0`
- runtime-selected native comparator pointer parity
- runtime-selected typed C ABI comparator pointer parity across ascending and descending sorted slices
- runtime-selected raw native comparator pointer parity
- runtime-selected raw C ABI comparator pointer parity, including descending-order lookup, pointer-return duplicate hits, mutable write-through, and null misses
- representative lookup work stays inside a bounded binary-search comparison budget for both typed and raw lookup paths

The current packet intentionally keeps its representative sorted inputs inline in `zigux/tests/phase6_bsearch.zig` instead of a separate fixture module so the helper bundle stays small and directly reviewable, and the same focused replay now carries the bounded comparison-budget evidence instead of a dedicated `phase6_bsearch_perf` route.

## Non-goals

This slice does not yet claim:

- lower-bound or upper-bound helpers
- duplicate-key stability guarantees beyond matching the kernel-style found-or-null contract
- standalone nanosecond ceilings or a dedicated `phase6_bsearch_perf` route beyond the bundled comparison-budget replay
- record-style raw `member_size` parity beyond the module-local `lib/bsearch.zig` self-test packet

## Next bounded step

Keep the next Phase 6 follow-up inside the existing bsearch helper-local packet. Reopen this slice only if fresh repo inspection finds a concrete new `bsearch.c` parity, comparator-alias, comparison-budget, or packet-alignment drift inside `lib/bsearch.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, or the shared bundled gates that already cover this parked helper. If the next real gap is the missing record-style raw `member_size` replay inside the focused Phase 6 packet, add that bounded test directly to `zigux/tests/phase6_bsearch.zig` rather than widening into a separate fixture or perf route.
