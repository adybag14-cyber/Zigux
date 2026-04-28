# Phase 6 Checksum Slice

This document starts a bounded Phase 6 leaf-helper port for Zigux.

## Status

- `PHASE6_STATUS=active`
- `PHASE6_SLICE=checksum-leaf-helper`
- scope: first low-risk checksum helper only
- product boundary:
  - `lib/checksum.zig`
  - `zigux/tests/phase6_checksum.zig`
  - `zigux/tests/fixtures/phase6_checksum_vectors.zig`
  - `zigux/tests/phase6_build.zig`
  - `zigux/Makefile`

## Why this slice exists

Phase 6 is where Zigux can start proving low-risk in-kernel helper ports without stepping into runtime-core or driver complexity.

`lib/checksum.c` is a good first slice because it is:

- leaf-oriented
- math-sensitive enough to justify a focused gate
- small enough to validate without inventing a broad new subsystem

## Gates

1. run the focused Zig checksum tests
- `zig build test --build-file zigux/tests/phase6_build.zig`

2. keep the helper wired through the Zigux convenience target
- `make -C zigux phase6`

3. replay the checksum perf sanity harness for this math-sensitive helper
- `make -C zigux phase6-checksum-perf`

## Current parity surface

The current checksum helper surface exercised by this slice covers:

- `add`
- `sub`
- `shift`
- `blockAdd`
- `blockSub`
- `from32to16`
- `fold`
- `tcpUdpNofold`
- `partial`
- `compute`

The current tests check:

- fixture-backed checksum vectors for empty, even, odd, and carry-heavy inputs
- incremental partial-sum chaining across even and odd fragment boundaries
- non-zero seeded `partial` accumulation parity across odd, carry-heavy, and pre-folded seed inputs
- a tiny KUnit-inspired carry-discipline matrix covering all-ones and no-spurious-carry seeded cases
- pseudo-header accumulation parity between `tcpUdpNofold` and manual `partial` plus `blockAdd`
- a replayable perf-sanity harness reports representative checksum cost per call and per byte for a fixture-backed deterministic packet matrix
- that perf harness also compares the helper against its own widened-accumulator reference path and rejects regressions that exceed the fixture-backed slowdown budget for the current packet sizes

The fixture layer stays intentionally small. It names representative Phase 6 parity cases in one place, now also owns the deterministic perf corpus plus relative slowdown ceilings consumed by `zigux/tests/phase6_checksum_perf.zig`, and borrows a small carry-discipline shape from `lib/tests/checksum_kunit.c` without claiming a full KUnit surface port.

## Non-goals

This slice does not yet claim:

- arch-specific assembly fast paths
- kbuild integration into the kernel proper
- performance equivalence across all architectures

## Next bounded step

Checksum now has a small KUnit-inspired carry-discipline foothold alongside the existing compute, composition, seeded-partial, pseudo-header, and relative perf-gate surfaces. The next honest decision is whether that evidence is now enough to park this Phase 6 leaf-helper lane unless a future external parity artifact becomes clearly worthwhile.
