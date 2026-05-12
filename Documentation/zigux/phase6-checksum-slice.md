# Phase 6 Checksum Slice

## Status
- `PHASE6_STATUS=parked`
- `PHASE6_SLICE=checksum-leaf-helper`
- helper anchor: `lib/checksum.zig`

## Review Surface
- `zigux/tests/phase6_checksum.zig`
- `zigux/tests/phase6_checksum_perf.zig`
- `zigux/tests/phase6_checksum_c_parity.zig`
- `zigux/tests/fixtures/phase6_checksum_vectors.zig`
- `zigux/tests/fixtures/phase6_checksum_c_harness.c`
- `scripts/zigux/check-phase6-checksum-c-parity.py`
- `scripts/zigux/check-phase6-perf-threshold-markers.py`
- direct local C parity rerun route: `python3 scripts/zigux/check-phase6-checksum-c-parity.py`
- Linux-style C parity rerun route: `make -C zigux phase6-checksum-c-parity`
- exact threshold marker rerun route: `python3 scripts/zigux/check-phase6-perf-threshold-markers.py`
- direct local perf rerun route: `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe`
- Linux-style perf rerun route: `make -C zigux phase6-checksum-perf`
- exact perf packet: `zigux/tests/fixtures/phase6_checksum_vectors.zig` still pins `64B` at `iterations = 200_000` and `1501B` at `iterations = 12_000`, with `max_slowdown_pct = 150` for both cases
- emitted perf evidence: `zigux/tests/phase6_checksum_perf.zig` still prints the per-case iterations, helper and reference nanoseconds, slowdown percentages, threshold percentages, per-case `pass` or `fail`, and the aggregate `PHASE6_CHECKSUM_PERF=pass|fail` result for the current two-case packet
- fixture-backed carry-discipline and imported KUnit random-prefix replays for all-ones prefixes and no-spurious-carry seeded cases
- the exported `add16` and `sub16` helper surface is live in `lib/checksum.zig`, but the current checksum-owned fixture and parity packet still does not carry dedicated 16-bit wrap and borrow rows for those helpers yet
- IPv4 and IPv6 pseudo-header accumulation parity between the dedicated helper paths and manual `partial` plus `blockAdd` composition
- incremental checksum replacement parity for payload word updates, 16-bit IPv4 header field replacement, diff-based checksum repair, and 32-bit IPv4 address replacement

## Next Step
Leave this slice parked unless a fresh checksum packet reread shows helper-local drift across the slice note, dedicated C parity evidence, or the dedicated slowdown gate on current `master`. If it reopens, rerun `python3 scripts/zigux/check-phase6-checksum-c-parity.py` and `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe` first, then keep the repair inside one checksum-owned packet surface such as adding dedicated `add16` and `sub16` carry rows to `zigux/tests/fixtures/phase6_checksum_vectors.zig` and replaying them through `zigux/tests/phase6_checksum.zig` plus `zigux/tests/phase6_checksum_c_parity.zig` instead of widening into shared Phase 6 routing or another helper lane.
