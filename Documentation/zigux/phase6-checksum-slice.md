# Phase 6 Checksum Slice

## Status
- `PHASE6_STATUS=parked_reviewable`
- `PHASE6_SLICE=checksum-leaf-helper`
- roadmap anchor: `lib/checksum.c`
- helper anchor: `lib/checksum.zig`
- shared packet note: `Documentation/zigux/phase6-helper-parity-catalog.md`
- shared perf note: `Documentation/zigux/phase6-perf-gate-survey.md`
- current `master` keeps `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`
- current `master` still keeps `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`
- current routed build packet now defines checksum helper and perf steps in `zigux/tests/phase6_build.zig`, while `zigux/Makefile` still advertises `phase6-checksum-c-parity` and `phase6-checksum-perf` phony routes without corresponding target bodies

## Review Surface
- present helper-owned packet: `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`
- still-present direct C parity scaffolding: `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`
- direct focused helper replay route: `zig build test --build-file zigux/tests/phase6_build.zig`
- direct focused perf route: `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`
- direct local C parity checker route: `python3 scripts/zigux/check-phase6-checksum-c-parity.py`
- built-in parity-script self-test route: `python3 scripts/zigux/check-phase6-checksum-c-parity.py --self-test`
- route nuance note: the checksum helper-owned replay and slowdown gate are readable from the committed helper packet again, but the shared `zigux/Makefile` and workflow surfaces still need their own route-truthfulness follow-up before reviewers should treat those wrappers as equivalent packet summaries
- current review posture: parked reviewable; the checksum roadmap anchor now keeps the helper-owned replay, slowdown gate, and direct C parity scaffolding readable on current `master`, while the remaining gap has narrowed to shared route inventory truthfulness rather than a missing checksum helper packet

## Next Step
Keep this lane parked unless a future checksum follow-up finds helper-local drift in `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, or `zigux/tests/fixtures/phase6_checksum_vectors.zig`.

Fresh repo-first reread on current `master` shows the earlier helper-packet absence is now closed inside the checksum-owned surfaces themselves. If this lane reopens soon, prefer the next helper-local checksum drift or a separate shared-route truthfulness repair in `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, `zigux/tests/phase6_helper_parity_manifest.json`, `zigux/Makefile`, or `.github/workflows/zigux-bootstrap.yml` instead of restaging this now-restored helper packet as missing again.
