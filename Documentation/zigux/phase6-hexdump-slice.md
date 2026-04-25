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
- already partially ported, with the committed Phase 6 harness now covering the formatter path too

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
- `hexDumpToBuffer`

The current tests check:

- mixed-case hex digit decoding
- encode/decode round-trips on bounded fixtures
- malformed source and destination handling
- kernel-style one-line hex and ASCII formatting
- native-endian grouped output for 2, 4, and 8 byte cases
- normalization behavior for rowsize and groupsize fallback cases lifted from `lib/test_hexdump.c`
- empty-buffer required-length behavior for normalized fallback paths
- truncation behavior while still reporting the full required line length

## Non-goals

This slice does not yet claim:

- printk-facing dump formatting helpers
- kernel logging integration
- full runtime KUnit integration or C-vs-Zig fixture generation

## Next bounded step

Decide whether to add a fixture-producing C parity harness under `zigux/tests/fixtures/` for `lib/test_hexdump.c`-style vectors, or close this helper lane and move to the next unfinished Phase 6 leaf helper.
