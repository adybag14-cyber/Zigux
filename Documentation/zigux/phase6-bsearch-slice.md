# Phase 6 Bsearch Slice

This document starts a bounded Phase 6 leaf-helper validation slice for Zigux.

## Status

- `PHASE6_STATUS=parked`
- `PHASE6_SLICE=bsearch-leaf-helper`
- scope: first low-risk binary-search helper coverage only
- lane state: helper and fixture slice landed; parked unless a new `bsearch.c` parity issue appears
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

## Current parity surface

The current bsearch helper surface exercised by this slice covers:

- `searchIndex`
- `search`

The current tests check:

- integer-key hits at the beginning, middle, and end of a sorted slice
- misses below, between, and above known values
- heterogeneous-key lookup where the key type differs from the element type
- pointer-return parity for successful lookups
- duplicate-key found-or-null parity without claiming stable duplicate selection
- representative lookup work stays inside a bounded binary-search comparison budget

## Non-goals

This slice does not yet claim:

- lower-bound or upper-bound helpers
- duplicate-key stability guarantees beyond matching the kernel-style found-or-null contract
- performance benchmarking

## Next bounded step

Keep the next Phase 6 follow-up inside the shared bundled `base64`, `bsearch`, `checksum`, and `hexdump` packet already gated by `zigux/tests/phase6_build.zig` and `make -C zigux phase6`. Reopen this slice only if fresh repo inspection finds a concrete new `bsearch.c` parity gap inside `lib/bsearch.zig`, `zigux/tests/phase6_bsearch.zig`, or that existing bundled gate.
