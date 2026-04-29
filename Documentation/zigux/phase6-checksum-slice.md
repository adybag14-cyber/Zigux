# Phase 6 Checksum Slice

This document reserves a bounded Phase 6 leaf-helper port for Zigux.

## Status

- `PHASE6_STATUS=planned`
- `PHASE6_SLICE=checksum-leaf-helper`
- scope: first low-risk checksum helper only
- live `master` currently ships the review note only; the code and harness files below are still the intended product boundary, not a landed surface:
  - `lib/checksum.zig`
  - `zigux/tests/phase6_checksum.zig`
  - `zigux/tests/fixtures/phase6_checksum_vectors.zig`
  - `zigux/tests/phase6_build.zig`
  - `zigux/Makefile`

## Why this slice exists

Phase 6 is where Zigux can start proving low-risk in-kernel helper ports without stepping into runtime-core or driver complexity.

`lib/checksum.c` is still a good first slice because it is:

- leaf-oriented
- math-sensitive enough to justify a focused gate
- small enough to validate without inventing a broad new subsystem

## Review Gate

Before this slice can be called active, live `master` needs a bounded checksum packet that lands all of the following together:

1. the helper surface in `lib/checksum.zig`
2. focused parity coverage in `zigux/tests/phase6_checksum.zig`
3. any imported or hand-authored checksum fixtures in `zigux/tests/fixtures/phase6_checksum_vectors.zig`
4. a Phase 6 build entry in `zigux/tests/phase6_build.zig`
5. the Zigux convenience targets in `zigux/Makefile`

Until those files exist on `master`, do not claim shipped checksum parity, shipped perf gating, or completed helper coverage from this note alone.

## Planned Parity Surface

Once the bounded checksum packet lands, the first honest parity target should stay narrow and reviewable. The intended starter surface remains:

- `add`
- `sub`
- `shift`
- `blockAdd`
- `blockSub`
- `from32to16`
- `fold`
- `unfold`
- `replaceByDiff`
- `replace4`
- `replace2`
- `replace`
- `tcpUdpNofold`
- `partial`
- `compute`

## Planned Gates

Once the helper and tests exist, the intended verification path is:

1. run the focused Zig checksum tests
- `zig build test --build-file zigux/tests/phase6_build.zig`

2. keep the helper wired through the Zigux convenience target
- `make -C zigux phase6`

3. replay the checksum perf sanity harness for this math-sensitive helper
- `make -C zigux phase6-checksum-perf`

The first landing should keep its fixture layer intentionally small and only claim parity that is directly backed by checked-in vectors, focused helper tests, and any shipped perf ceiling data.

## Non-goals

This slice does not yet claim:

- arch-specific assembly fast paths
- kbuild integration into the kernel proper
- performance equivalence across all architectures

## Next bounded step

The next honest checksum step is to land the first real `lib/checksum.zig` packet with a minimal parity surface and directly coupled tests, then flip this note from planned to active only after those files exist on live `master`.
