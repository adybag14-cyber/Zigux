# Phase 6 Checksum Slice

## Status
- `PHASE6_STATUS=blocked`
- `PHASE6_SLICE=checksum-leaf-helper`
- roadmap anchor: `lib/checksum.c`
- helper anchor expected by the shared packet: `lib/checksum.zig`
- current `master` still lacks the broader checksum helper packet under `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`
- current `master` still keeps the direct checksum C parity scaffolding under `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`

## Review Surface
- present checksum-owned direct C parity packet: `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`
- stale shared routes that still point at the absent broader checksum helper packet: `zigux/tests/phase6_helper_parity_manifest.json`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`
- currently missing helper-local helper and perf packet: `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`
- direct local C parity rerun route once the helper packet is restored: `python3 scripts/zigux/check-phase6-checksum-c-parity.py`
- Linux-style C parity rerun route once the helper packet is restored: `make -C zigux phase6-checksum-c-parity`
- direct local perf rerun route once the helper packet is restored: `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe`
- Linux-style perf rerun route once the helper packet is restored: `make -C zigux phase6-checksum-perf`
- the checked-in direct C parity surface is not currently runnable as a complete packet because `zigux/tests/phase6_checksum_c_parity.zig` still imports the absent `lib/checksum.zig` helper and the absent `zigux/tests/fixtures/phase6_checksum_vectors.zig` fixture module
- current `master` cannot honestly claim fixture-backed carry-discipline, `tcpUdpV6Nofold` pseudo-header parity, or `replaceByDiff` replay coverage because the checksum-owned helper and fixture-backed replay packet are absent even though the direct parity scaffolding remains checked in and the stale shared manifest, build, Makefile, and workflow surfaces still advertise the broader checksum helper packet
- this slice is blocked until the checksum helper packet is restored or the shared packet routes are rewritten to match the absent helper state

## Next Step
Refresh against a fresh `master` base and choose one bounded repair: either restore `lib/checksum.zig` plus the checksum-owned helper and fixture packet and rerun `python3 scripts/zigux/check-phase6-checksum-c-parity.py` plus `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe`, or retell the shared manifest, build, Makefile, and workflow surfaces so they stop advertising a checksum helper packet that the committed tree does not contain.
