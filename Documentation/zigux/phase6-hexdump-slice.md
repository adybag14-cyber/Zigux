# Phase 6 Hexdump Slice

This document records a bounded Phase 6 leaf-helper validation slice for Zigux.

## Status

- `PHASE6_STATUS=parked`
- `PHASE6_SLICE=hexdump-leaf-helper`
- scope: first low-risk hexdump helper coverage only
- lane state: helper, fixture, and dedicated perf gate slices landed; parked unless a new `hexdump.c` parity issue appears
- product boundary:
  - `lib/hexdump.zig`
  - `zigux/tests/phase6_hexdump.zig`
  - `zigux/tests/phase6_hexdump_perf.zig`
  - `zigux/tests/fixtures/phase6_hexdump_vectors.zig`
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

2. run the dedicated hexdump perf gate when the formatter-sensitive lane reopens
- `zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe`
- `make -C zigux phase6-hexdump-perf`

3. keep the helper wired through the Zigux convenience targets
- `make -C zigux phase6`

## Current parity surface

The current hexdump helper surface exercised by this slice covers:

- `hexAscHi`
- `hexAscLo`
- `hexAscUpperHi`
- `hexAscUpperLo`
- `hexBytePack`
- `hexBytePackUpper`
- `hexToBin`
- `hex2bin`
- `bin2hex`
- `hexDumpLineLength`
- `hexDumpToBuffer`

The current tests check:

- mixed-case hex digit decoding
- lowercase and uppercase nibble helpers stay aligned with the byte-pack paths on representative inputs
- encode/decode round-trips on bounded fixtures
- malformed source and destination handling, including undersized uppercase byte-pack buffers
- serialized fixture vectors derived from `lib/test_hexdump.c`
- serialized required-length vectors for `hexDumpLineLength` and zero-buffer `hexDumpToBuffer`
- kernel-style one-line hex and ASCII formatting
- native-endian grouped output for 2, 4, and 8 byte cases
- normalization behavior for rowsize and groupsize fallback cases lifted from `lib/test_hexdump.c`
- empty-buffer required-length behavior for normalized fallback paths
- truncation behavior while still reporting the full required line length
- the non-truncating helper path now uses a direct full-buffer formatter so the grouped ASCII perf replays do not pay the truncating writer's per-byte bounds checks
- a dedicated perf replay that benchmarks the existing four-case perf fixture packet against the committed `fixtures.prepareExpectedLine(...)` reference path

The current perf fixture packet in `zigux/tests/fixtures/phase6_hexdump_vectors.zig` stays bounded to:

- `16B-plain-g1`
- `32B-ascii-g2`
- `16B-ascii-g4`
- `16B-ascii-g8`

## Non-goals

This slice does not yet claim:

- printk-facing dump formatting helpers
- kernel logging integration
- full runtime KUnit integration or C-vs-Zig fixture generation

## Next bounded step

Keep the next Phase 6 follow-up inside the shared bundled `base64`, `bsearch`, `checksum`, and `hexdump` packet already gated by `zigux/tests/phase6_build.zig` and `make -C zigux phase6`. Reopen this slice only if fresh repo inspection finds a concrete new `hexdump.c` parity gap inside `lib/hexdump.zig`, `zigux/tests/phase6_hexdump.zig`, `zigux/tests/phase6_hexdump_perf.zig`, the shared fixture module, or that existing bundled gate.