# Phase 6 Hexdump Slice

This document records the bounded Phase 6 leaf-helper validation slice for Zigux.

## Status

- `PHASE6_STATUS=parked`
- `PHASE6_SLICE=hexdump-leaf-helper`
- scope: first low-risk hexdump helper coverage only
- lane posture: parked after the current parity surface cleared the bounded helper goal
- product boundary:
  - `lib/hexdump.zig`
  - `zigux/tests/phase6_hexdump.zig`
  - `zigux/tests/phase6_hexdump_perf.zig`
  - `zigux/tests/phase6_hexdump_c_parity.zig`
  - `zigux/tests/fixtures/phase6_hexdump_vectors.zig`
  - `zigux/tests/fixtures/phase6_hexdump_c_harness.c`
  - `scripts/zigux/check-phase6-hexdump-c-parity.py`
  - `zigux/tests/phase6_build.zig`
  - `zigux/Makefile`

## Why this slice exists

Phase 6 is where Zigux can keep proving low-risk in-kernel helper ports without stepping into runtime-core or driver complexity.

`lib/hexdump.c` is a good Phase 6 slice because it is:

- leaf-oriented
- string and formatting sensitive enough to justify a focused gate
- already ported with the committed Phase 6 harness covering the formatter path too

## Gates

1. run the shared Phase 6 validator-first handoff before helper-local replay
- `python3 scripts/zigux/validate-phase6.py --self-test`
- `make -C zigux phase6-validate`

2. run the bounded external C-vs-Zig parity spot check
- `python3 scripts/zigux/check-phase6-hexdump-c-parity.py --self-test`
- `python3 scripts/zigux/check-phase6-hexdump-c-parity.py`

3. run the shared checksum-plus-hexdump perf-marker guard when touching perf reporting, thresholds, or reference-path wording
- `python3 scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py --self-test`
- `python3 scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py`

4. run the focused Zig Phase 6 helper tests
- `zig build test --build-file zigux/tests/phase6_build.zig`

5. keep the helper wired through the Zigux convenience target
- `make -C zigux phase6`

6. replay the hexdump perf sanity harness when reviewing formatter-cost drift
- `zig build hexdump-perf --build-file zigux/tests/phase6_build.zig`
- or `make -C zigux phase6-hexdump-perf`

## Current parity surface

The current hexdump helper surface exercised by this slice covers:

- `hexToBin`
- `hexBytePack`
- `hexBytePackUpper`
- `hex2bin`
- `bin2hexAppend`
- `bin2hex`
- `bin2hexAppendUpper`
- `bin2hexUpper`
- `hexDumpLineLength`
- `hexDumpToBuffer`

The current tests check:

- uppercase whole-buffer hex encoding for a representative byte packet
- append-style whole-buffer encoding that can chain lowercase and uppercase segments without recomputing offsets
- direct nibble helper coverage for lowercase and uppercase hex digits
- direct byte-pack helper coverage for lowercase and uppercase output plus the short-buffer contract
- mixed-case hex digit decoding
- encode/decode round-trips on bounded fixtures
- malformed source and destination handling
- serialized fixture vectors derived from `lib/test_hexdump.c`
- serialized required-length vectors for `hexDumpLineLength` and zero-buffer `hexDumpToBuffer`
- kernel-style one-line hex and ASCII formatting
- native-endian grouped output for 2, 4, and 8 byte cases, including the previously missing 4-byte review gate
- exact grouped ASCII output for native-endian 2-byte, 4-byte, and 8-byte formatter cases on the representative 16-byte packet
- normalization behavior for rowsize and groupsize fallback cases lifted from `lib/test_hexdump.c`
- shared normalization ownership stays in `zigux/tests/fixtures/phase6_hexdump_vectors.zig`, where `normalizedRowsize()`, `normalizedGroupsizeForLen()`, and `prepareExpectedLine(...)` keep the parity, overflow, required-length, and perf replays on one committed corpus path
- empty-buffer required-length behavior for normalized fallback paths
- truncation behavior while still reporting the full required line length
- exact `required + 1` caller-buffer coverage for the non-truncating formatter path, keeping the grouped plain and grouped ASCII fast path aligned with the same fixture output and NUL-termination contract as the roomy replay
- a replayable perf-sanity harness reports representative dump cost per call and per byte for plain, grouped, and ASCII formatter paths through the shared `zigux/tests/fixtures/phase6_hexdump_vectors.zig` perf-case table, including the native-endian 4-byte and 8-byte grouped ASCII branches
- the same perf harness now measures helper output against the committed `fixtures.prepareExpectedLine(...)` reference path, keeping `16B-plain` at `max_slowdown_pct = 175` while the grouped ASCII `32B-ascii-g2` and `16B-ascii-g4` replays use `max_slowdown_pct = 550` and the wider native-endian `16B-ascii-g8` replay uses `max_slowdown_pct = 600`
- the shared `python3 scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py` guard now keeps that perf packet fail-closed around the per-call, per-byte, slowdown, required-length, and reference-path markers before broader Phase 6 replay claims stay green
- an external C-vs-Zig spot check through `python3 scripts/zigux/check-phase6-hexdump-c-parity.py`, `zigux/tests/phase6_hexdump_c_parity.zig`, and `zigux/tests/fixtures/phase6_hexdump_c_harness.c`, now covering 29 deterministic lines across mixed-case decode, lower and upper whole-buffer encode, append-style encode, four length probes, ten formatter outputs, and four truncation paths, including the native-endian grouped-2 plain and ASCII formatter lines that were previously only proven inside the Zig-side review packet

This is enough evidence to leave the bounded hexdump helper lane parked unless a concrete new parity, perf, or directly coupled review-packet gap appears in the live repo.

## Non-goals

This slice does not yet claim:

- printk-facing dump formatting helpers
- kernel logging integration
- generated external parity fixture snapshots

## Next bounded step

Leave the hexdump helper lane parked unless fresh repo inspection finds a concrete parity, perf, or directly coupled review-packet drift inside `lib/hexdump.zig`, `zigux/tests/phase6_hexdump.zig`, `zigux/tests/phase6_hexdump_perf.zig`, `zigux/tests/phase6_hexdump_c_parity.zig`, `zigux/tests/fixtures/phase6_hexdump_vectors.zig`, `zigux/tests/fixtures/phase6_hexdump_c_harness.c`, `scripts/zigux/check-phase6-hexdump-c-parity.py`, or the shared Phase 6 packet. Current repo evidence shows the widened external grouped-2 parity packet, the shared catalog, the machine-readable manifest, and the shared validator all agree on the same 29-line hexdump portability surface and parked shared-packet posture. The next honest same-family follow-up should therefore stay narrow to future shared-packet drift rather than reopening `lib/hexdump.zig` or its directly coupled hexdump parity and perf harnesses.
