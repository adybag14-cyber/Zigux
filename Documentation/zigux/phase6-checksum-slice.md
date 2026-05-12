# Phase 6 Checksum Slice

## Status
- `PHASE6_STATUS=blocked`
- `PHASE6_SLICE=checksum-leaf-helper`
- roadmap anchor: `lib/checksum.c`
- helper anchor expected by the shared packet: `lib/checksum.zig`
- current `master` lacks `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, `zigux/tests/phase6_checksum_c_parity.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`

## Review Surface
- present checksum-owned checker surface: `scripts/zigux/check-phase6-checksum-c-parity.py`
- stale shared routes that still point at the absent checksum packet: `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`
- currently missing helper-local packet: `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_vectors.zig`, and `zigux/tests/fixtures/phase6_checksum_c_harness.c`
- direct local C parity rerun route once the helper packet is restored: `python3 scripts/zigux/check-phase6-checksum-c-parity.py`
- Linux-style C parity rerun route once the helper packet is restored: `make -C zigux phase6-checksum-c-parity`
- direct local perf rerun route once the helper packet is restored: `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe`
- Linux-style perf rerun route once the helper packet is restored: `make -C zigux phase6-checksum-perf`
- current `master` cannot honestly claim fixture-backed carry-discipline, `tcpUdpV6Nofold` pseudo-header parity, or `replaceByDiff` replay coverage because the checksum-owned Zig test packet is absent from the tree
- this slice is documentary only until the checksum helper packet is restored or the shared packet routes are rewritten to match the absent helper state

## Next Step
Refresh against a fresh `master` base and choose one bounded repair: either restore `lib/checksum.zig` plus the checksum-owned test packet and rerun `python3 scripts/zigux/check-phase6-checksum-c-parity.py` plus `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe`, or retell the shared build, Makefile, workflow, and manifest surfaces so they stop advertising a checksum packet that the committed tree does not contain.
