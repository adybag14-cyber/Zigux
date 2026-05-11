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
- direct local C parity rerun route: `python3 scripts/zigux/check-phase6-checksum-c-parity.py`
- Linux-style C parity rerun route: `make -C zigux phase6-checksum-c-parity`
- fixture-backed carry-discipline and imported KUnit random-prefix replays for all-ones prefixes and no-spurious-carry seeded cases
- IPv4 and IPv6 pseudo-header accumulation parity between the dedicated helper paths and manual `partial` plus `blockAdd` composition
- incremental checksum replacement parity for payload word updates, 16-bit IPv4 header field replacement, diff-based checksum repair, and 32-bit IPv4 address replacement
- `make -C zigux phase6-checksum-perf`

## Next Step
Leave this slice parked unless helper semantics, direct C parity evidence, or the dedicated slowdown gate drifts on current `master`.
