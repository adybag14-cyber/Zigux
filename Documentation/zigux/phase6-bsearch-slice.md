# Phase 6 Bsearch Slice

This document starts a bounded Phase 6 leaf-helper validation slice for Zigux.

## Status

- `PHASE6_STATUS=parked`
- `PHASE6_SLICE=bsearch-leaf-helper`
- scope: first low-risk binary-search helper coverage only
- lane state: helper slice landed; parked unless a new `bsearch.c` parity issue appears
- product boundary:
  - `lib/bsearch.zig`
  - `zigux/tests/phase6_bsearch.zig`
  - `zigux/tests/phase6_build.zig`
  - `zigux/Makefile`

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

3. keep the shared Phase 6 surface checker aligned with this slice
- `make -C zigux phase6-validate`

## Current parity surface

The current bsearch helper surface exercised by this slice covers:

- `searchIndex`
- `search`
- `searchMutable`
- `bsearchIndex`
- `bsearch`
- `bsearchMutable`

The current tests check:

- integer-key hits at the beginning, middle, and end of a sorted slice
- misses below, between, and above known values
- comparator-driven descending-order lookup without widening the helper surface
- heterogeneous-key lookup where the key type differs from the element type
- pointer-return parity for successful typed lookups
- mutable typed and raw lookup write-through parity
- duplicate-key found-or-null parity without claiming stable duplicate selection
- representative lookup work stays inside a bounded binary-search comparison budget for both typed and raw lookup paths
- raw empty-input parity, including that the comparator is not invoked when `num_members == 0`
- runtime-selected native comparator pointer parity
- runtime-selected C ABI comparator pointer parity
- runtime-selected raw native comparator pointer parity
- runtime-selected raw C ABI comparator pointer parity, including descending-order lookup, pointer-return duplicate hits, mutable write-through, and null misses

The current packet intentionally keeps its representative sorted inputs inline in `zigux/tests/phase6_bsearch.zig` instead of a separate fixture module so the helper bundle stays small and directly reviewable.

## Non-goals

This slice does not yet claim:

- lower-bound or upper-bound helpers
- duplicate-key stability guarantees beyond matching the kernel-style found-or-null contract
- standalone performance benchmarking outside the bundled comparison-budget replay

## Next bounded step

Keep the next Phase 6 follow-up inside the shared bundled `base64`, `bsearch`, `checksum`, and `hexdump` packet already gated by `zigux/tests/phase6_build.zig`, `make -C zigux phase6`, and `make -C zigux phase6-validate`. Reopen this slice only if fresh repo inspection finds a concrete new `bsearch.c` parity gap inside `lib/bsearch.zig`, `zigux/tests/phase6_bsearch.zig`, or that existing bundled gate.
