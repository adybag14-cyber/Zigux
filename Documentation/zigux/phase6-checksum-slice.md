# Phase 6 Checksum Slice

This document starts a bounded Phase 6 leaf-helper port for Zigux.

## Status

- `PHASE6_STATUS=active`
- `PHASE6_SLICE=checksum-leaf-helper`
- scope: first low-risk checksum helper only
- product boundary:
  - `lib/checksum.zig`
  - `zigux/tests/phase6_checksum.zig`
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

- IPv4-header checksum parity through the committed helper API
- incremental partial-sum chaining across even and odd fragment boundaries
- pseudo-header accumulation parity between `tcpUdpNofold` and manual `partial` plus `blockAdd`

## Non-goals

This slice does not yet claim:

- arch-specific assembly fast paths
- kbuild integration into the kernel proper
- performance equivalence across all architectures
