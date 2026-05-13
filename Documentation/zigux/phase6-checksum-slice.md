# Phase 6 Checksum Slice

## Status
- `PHASE6_STATUS=parked`
- `PHASE6_SLICE=checksum-leaf-helper`
- roadmap anchor: `lib/checksum.c`
- helper anchor: `lib/checksum.zig`
- current `master` carries the broader checksum helper packet under `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`
- current `master` also carries the direct checksum C parity packet under `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`

## Review Surface
- present checksum helper packet: `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`
- present checksum-owned direct C parity packet: `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`
- shared Phase 6 routes that should stay aligned with the live checksum packet: `zigux/tests/phase6_helper_parity_manifest.json`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, and `Documentation/zigux/phase6-perf-gate-survey.md`
- direct local C parity rerun route: `python3 scripts/zigux/check-phase6-checksum-c-parity.py`
- Linux-style C parity rerun route: `make -C zigux phase6-checksum-c-parity`
- direct local perf rerun route: `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe`
- Linux-style perf rerun route: `make -C zigux phase6-checksum-perf`
- the current live packet keeps the checksum helper, the fixture-backed replay, the perf gate, and the direct C parity bridge under one checksum-owned review surface, so this slice should not describe the helper packet as absent unless those files truly disappear from current `master`
- the bounded risk in this lane is review-surface drift between this note and the live checksum packet, not a missing checksum helper implementation

## Next Step
Leave this slice parked unless a fresh checksum packet reread finds real drift across the helper, the fixture-backed replay, the direct C parity packet, or the perf routes. If the lane reopens, rerun `python3 scripts/zigux/check-phase6-checksum-c-parity.py` and `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe` first, then keep the repair to one checksum-owned surface only.
