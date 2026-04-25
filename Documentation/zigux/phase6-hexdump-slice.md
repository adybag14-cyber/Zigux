# Phase 6 Hexdump Slice

This document starts a bounded Phase 6 leaf-helper validation slice for Zigux.

## Status

- `PHASE6_STATUS=active`
- `PHASE6_SLICE=hexdump-leaf-helper`
- scope: first low-risk hexdump helper coverage only
- product boundary:
  - `lib/hexdump.zig`
  - `zigux/tests/phase6_hexdump.zig`
  - `zigux/tests/phase6_build.zig`
  - `zigux/Makefile`

## Why this slice exists

Phase 6 is where Zigux can keep proving low-risk in-kernel helper ports without stepping into runtime-core or driver complexity.

`lib/hexdump.c` is a good next slice because it is:

- leaf-oriented
- string and formatting sensitive enough to justify a focused gate
- already partially ported, but not yet wired into the committed Phase 6 harness

## Gates

1. run the focused Zig Phase 6 helper tests
- `zig build test --build-file zigux/tests/phase6_build.zig`

2. keep the helper wired through the Zigux convenience target
- `make -C zigux phase6`

## Current parity surface

The current hexdump helper surface exercised by this slice covers:

- `hexToBin`
- `hex2bin`
- `bin2hex`

The current tests check:

- mixed-case hex digit decoding
- encode/decode round-trips on bounded fixtures
- malformed source and destination handling

## Non-goals

This slice does not yet claim:

- parity for `hex_dump_to_buffer`
- printk-facing dump formatting helpers
- kernel logging integration

## Next bounded step

Port `hex_dump_to_buffer()` from `lib/hexdump.c` and lift a small deterministic subset of `lib/test_hexdump.c` into Zig parity fixtures.
