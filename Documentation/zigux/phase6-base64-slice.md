# Phase 6 Base64 Slice

## Status
- `PHASE6_STATUS=reviewable`
- `PHASE6_SLICE=base64-leaf-helper`
- helper anchor: `lib/base64.zig`
- shared packet note: `Documentation/zigux/phase6-helper-parity-catalog.md`
- current `master` keeps `lib/base64.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, and `zigux/tests/phase6_base64_perf.zig`
- current `master` still keeps the direct C parity packet: `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`

## Review Surface
- present focused helper replay, shared vectors, and dedicated slowdown gate: `lib/base64.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, and `zigux/tests/phase6_base64_perf.zig`
- present direct C parity packet: `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`
- direct focused helper replay route: `zig build test --build-file zigux/tests/phase6_build.zig`
- direct focused perf route: `zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig`
- direct local C parity checker route: `python3 scripts/zigux/check-phase6-base64-c-parity.py`
- built-in parity-script self-test route: `python3 scripts/zigux/check-phase6-base64-c-parity.py --self-test`
- helper-local perf note: the dedicated perf replay stays intentionally scoped to the shared committed payload plus the standard and URL-safe padded and unpadded branches; IMAP slowdown coverage remains parked until the fixture packet explicitly widens again

## Next Step
Keep this lane parked unless a future base64 follow-up finds a helper-local regression in `lib/base64.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_base64_perf.zig`, or `zigux/tests/fixtures/phase6_base64_vectors.zig`.
