# Phase 6 Bsearch Slice

This document starts a bounded Phase 6 leaf-helper validation slice for Zigux.

## Status

- `PHASE6_STATUS=parked`
- `PHASE6_SLICE=bsearch-leaf-helper`
- scope: parked helper-local bsearch parity and comparison-budget packet only
- lane state: helper slice landed; parked unless a new `bsearch.c` parity, comparison-budget, lower-bound companion, or packet-alignment drift appears
- product boundary:
  - `lib/bsearch.zig`
  - `zigux/tests/phase6_bsearch.zig`
  - `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`
  - `zigux/tests/phase6_build.zig`
  - `zigux/Makefile`
- evidence note: direct readback on `2026-05-08` inspected the current `lib/bsearch.c`, `lib/bsearch.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, and `zigux/tests/phase6_build.zig` packet so this slice stays limited to the shipped helper-local review surface instead of stale blob bookkeeping
- roadmap anchor note: the live `lib/bsearch.c` anchor is still a thin `__inline_bsearch(...)` wrapper, so the shipped Zigux packet keeps raw `bsearch` and `bsearchMutable` replay as the roadmap-facing surface while the typed helper entrypoints, lower-bound companions, and focused C ABI lower-bound replay keep the same comparator contract easier to inspect in one bounded packet instead of implying a separate direct C harness or timing-style perf gate

## Why this slice exists

Phase 6 is where Zigux can keep proving low-risk in-kernel helper ports without stepping into runtime-core or driver complexity.

`lib/bsearch.c` is a good next slice because it is:

- leaf-oriented
- small enough to validate with deterministic sorted inputs kept directly in the focused replay
- a clean API-parity target for comparator-driven helper behavior
- thin enough that the roadmap-facing parity claim can stay concentrated on the raw `bsearch` contract while Zig-only typed helpers and lower-bound companions keep the same comparison semantics easier to inspect in one bounded packet

## Gates

1. run the focused Zig Phase 6 helper tests
- `zig build test --build-file zigux/tests/phase6_build.zig`

2. keep the helper wired through the Zigux convenience target
- `make -C zigux phase6`

3. keep the helper-local comparison-budget replay aligned with the current helper packet
- `zigux/tests/phase6_bsearch.zig`

4. keep the focused lower-bound C ABI replay aligned with the current helper packet
- `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`

5. keep the shared Phase 6 surface checker aligned with this slice
- `make -C zigux phase6-validate`

## Current parity surface

The current bsearch helper surface exercised by this slice covers:

- `searchIndex`
- `search`
- `searchMutable`
- `lowerBoundIndex`
- `bsearchIndex`
- `bsearch`
- `bsearchMutable`
- `bsearchLowerBoundIndex`
- `Comparator`
- `CComparator`
- `RawComparator`
- `CRawComparator`

Within that surface, the roadmap-facing parity anchor remains the raw `bsearch` and `bsearchMutable` pair that mirrors the thin Linux wrapper, while `searchIndex`, `search`, `searchMutable`, `lowerBoundIndex`, `bsearchIndex`, and `bsearchLowerBoundIndex` stay helper-local companions that make the comparator contract, insertion-point behavior, and comparison-budget evidence directly reviewable without widening Phase 6 into another helper family.

The current tests check:

- integer-key hits at the beginning, middle, and end of a sorted slice
- misses below, between, and above known values
- comparator-driven descending-order lookup without widening the helper surface
- heterogeneous-key lookup where the key type differs from the element type
- pointer-return parity for successful typed lookups
- mutable typed and raw lookup write-through parity
- duplicate-key found-or-null parity without claiming stable duplicate selection
- typed and raw lower-bound insertion parity across duplicates, insertion edges, descending-order inputs, and packed-record `member_size` boundaries
- typed and raw empty-input parity, including that the comparator is not invoked when the typed slice is empty or `num_members == 0`
- runtime-selected native comparator pointer parity
- runtime-selected typed C ABI comparator pointer parity across ascending and descending sorted slices
- runtime-selected raw native comparator pointer parity
- focused typed and raw lower-bound C ABI parity across ascending and descending sorted inputs plus packed-record `member_size` boundaries through `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`
- runtime-selected raw C ABI comparator pointer parity, including descending-order lookup, pointer-return duplicate hits, mutable write-through, and null misses
- representative lookup work stays inside a bounded binary-search comparison budget for both typed and raw lookup paths
- raw record lookup parity that exercises `member_size` across packed record entries and mutable write-through directly in the focused Phase 6 packet
- raw `bsearch` and `bsearchMutable` replay stays explicit as the roadmap-facing wrapper surface while the typed helpers and lower-bound companions prove the same comparison semantics without needing a separate C harness packet

The current packet intentionally keeps its representative sorted inputs inline in `zigux/tests/phase6_bsearch.zig` instead of a separate fixture module so the helper bundle stays small and directly reviewable, and the same focused replay now carries the bounded comparison-budget evidence instead of a dedicated `phase6_bsearch_perf` route. The paired `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig` file keeps the lower-bound C ABI proof equally small and reviewable without widening the packet into a separate harness family.

## Non-goals

This slice does not yet claim:

- upper-bound helpers or broader search variants beyond the current search and lower-bound packet
- duplicate-key stability guarantees beyond matching the kernel-style found-or-null contract
- standalone nanosecond ceilings or a dedicated `phase6_bsearch_perf` route beyond the bundled comparison-budget replay
- a separate direct C harness, because the current roadmap anchor is still only the thin exported wrapper around `__inline_bsearch(...)`

## Next bounded step

Keep the next Phase 6 follow-up inside the existing bsearch helper-local packet. Reopen this slice only if fresh repo inspection finds a concrete new `bsearch.c` parity, lower-bound companion, comparator-alias, comparison-budget, or packet-alignment drift inside `lib/bsearch.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, or the shared bundled gates that already cover this parked helper.
