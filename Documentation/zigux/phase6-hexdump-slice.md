# Phase 6 Hexdump Slice

This document records the bounded Phase 6 leaf-helper validation slice for Zigux.

## Status

- `PHASE6_STATUS=active`
- `PHASE6_SLICE=hexdump-leaf-helper`
- scope: first low-risk hexdump helper coverage only
- lane posture: parked after the current parity surface cleared the bounded helper goal
- product boundary:
- `lib/hexdump.zig`
- `zigux/tests/phase6_hexdump.zig`
- `zigux/tests/fixtures/phase6_hexdump_vectors.zig`
- `zigux/tests/phase6_build.zig`
- `zigux/Makefile`

## Why this slice exists

Phase 6 is where Zigux can keep proving low-risk in-kernel helper ports without stepping into runtime-core or driver complexity.

`lib/hexdump.c` is a good Phase 6 slice because it is:

- leaf-oriented
- string and formatting sensitive enough to justify a focused gate
- already ported with the committed Phase 6 harness covering the formatter path too

## Gates

1. run the focused Zig Phase 6 helper tests
- `zig build test --build-file zigux/tests/phase6_build.zig`

2. keep the helper wired through the Zigux convenience target
- `make -C zigux phase6`

3. replay the hexdump perf sanity harness when reviewing formatter-cost drift
- `make -C zigux phase6-hexdump-perf`

## Current parity surface

The current hexdump helper surface exercised by this slice covers:

- `hexToBin`
- `hex2bin`
- `bin2hex`
- `bin2hexUpper`
- `hexDumpToBuffer`

The current tests check:

- uppercase whole-buffer hex encoding for a representative byte packet
- mixed-case hex digit decoding
- encode/decode round-trips on bounded fixtures
- malformed source and destination handling
- serialized fixture vectors derived from `lib/test_hexdump.c`
- serialized required-length vectors for `hexDumpLineLength` and zero-buffer `hexDumpToBuffer`
- kernel-style one-line hex and ASCII formatting
- native-endian grouped output for 2, 4, and 8 byte cases
- normalization behavior for rowsize and groupsize fallback cases lifted from `lib/test_hexdump.c`
- empty-buffer required-length behavior for normalized fallback paths
- truncation behavior while still reporting the full required line length
- a replayable perf-sanity harness reports representative dump cost per call and per byte for plain and ASCII formatter paths

This is enough evidence to leave the bounded hexdump helper lane parked unless a concrete new parity gap appears in the live repo.

## Non-goals

This slice does not yet claim:

- printk-facing dump formatting helpers
- kernel logging integration
- full runtime KUnit integration or C-vs-Zig fixture generation

## Next bounded step

Leave the hexdump helper lane parked and move future Phase 6 work to another unfinished helper family unless fresh repo inspection finds a concrete new parity, perf, or ABI gap in this exact slice.