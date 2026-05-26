# Phase 6 Hexdump Slice

## Status
- `PHASE6_STATUS=parked_reviewable`
- `PHASE6_SLICE=hexdump-leaf-helper`
- lane state: helper slice restored; parked unless helper-local formatting parity, overflow handling, grouped output alignment, perf-threshold rationale, or shared route drift reappears

## API Surface
- `hexAscHi`
- `hexAscLo`
- `hexAscUpperHi`
- `hexAscUpperLo`
- `hexBytePack`
- `hexBytePackUpper`
- `hexToBin`
- `hex2bin`
- `bin2hex`
- `bin2hexUpper`
- `hexDumpLineLength`
- `hexDumpToBuffer`
- snake-case and mixed-case alias exports through `hex_to_bin`, `hex2Bin`, `bin2Hex`, and `bin2HexUpper`

## Review Surface
- `lib/hexdump.zig`
- `zigux/tests/phase6_hexdump.zig`
- `zigux/tests/phase6_hexdump_perf.zig`
- `zigux/tests/phase6_hexdump_perf_matrix.zig`
- `zigux/tests/fixtures/phase6_hexdump_vectors.zig`
- `Documentation/zigux/phase6-hexdump-perf-refresh.md`
- `scripts/zigux/check-phase6-hexdump-packet.py`
- `scripts/zigux/check-phase6-hexdump-route.py`
- `zigux/tests/phase6_build.zig`
- `zigux/Makefile`
- `Documentation/zigux/phase6-helper-evidence-catalog.md`
- `zigux/tests/phase6_helper_parity_manifest.json`
- `zigux/tests/phase6_helper_evidence_manifest.json`

The review packet keeps the landed `hexAsc*`, `hexBytePack`, `hexBytePackUpper`, `bin2hexUpper`/`bin2HexUpper`, and `hexDumpLineLength` helper parity surface beside the focused helper replay, the perf replay, the exact perf-matrix preflight, and the route guards that keep the shared build and Makefile packet aligned.

This slice stays bounded because focused helper formatting parity plus a four-case fixture-backed slowdown matrix keep the shipped hexdump packet reviewable without widening this lane into checksum, base64, bsearch, threshold retuning beyond the documented cases, or broader Phase 6 reminder churn.

`zigux/tests/phase6_helper_parity_manifest.json` still records a four-case slowdown packet, and `make -C zigux phase6-hexdump-review` remains the bounded route that rechecks the hexdump review packet before the broader `phase6-perf` wrapper is reopened.

## Current Bounded Next Step
If this helper reopens, keep the next move inside `lib/hexdump.zig`, `zigux/tests/phase6_hexdump.zig`, `zigux/tests/phase6_hexdump_perf.zig`, `zigux/tests/phase6_hexdump_perf_matrix.zig`, `zigux/tests/fixtures/phase6_hexdump_vectors.zig`, `Documentation/zigux/phase6-hexdump-perf-refresh.md`, `scripts/zigux/check-phase6-hexdump-packet.py`, `scripts/zigux/check-phase6-hexdump-route.py`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, or this slice note only. The first safe follow-up after fresh repo inspection is rerunning `python3 scripts/zigux/check-phase6-hexdump-packet.py`, `python3 scripts/zigux/check-phase6-hexdump-route.py`, `zig build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig`, and `zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe`, then keeping any repair to one helper-local parity, perf-threshold, fixture, or route drift.
