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
- current wrapper nuance: the helper-owned perf gate is directly runnable through `zigux/tests/phase6_build.zig`, but the Linux-style `make -C zigux phase6-base64-perf` name still lives only in shared route inventory surfaces because current `zigux/Makefile` does not yet expose a committed target body
- direct local C parity checker route: `python3 scripts/zigux/check-phase6-base64-c-parity.py`
- built-in parity-script self-test route: `python3 scripts/zigux/check-phase6-base64-c-parity.py --self-test`
- helper-local perf note: the dedicated perf replay now covers the shared committed payload plus the standard, URL-safe, and IMAP padded and unpadded branches under the same helper-local slowdown thresholds

## Next Step
Keep this lane parked unless a future base64 follow-up finds helper-local regression in `lib/base64.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_base64_perf.zig`, or `zigux/tests/fixtures/phase6_base64_vectors.zig`, or lands the still-missing Linux-style `phase6-base64-perf` wrapper around that already-shipped perf replay.

Fresh repo-first reread on current `master` now shows the earlier shared-surface split is closed inside the helper-owned base64 packet itself: `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, and `zigux/tests/phase6_helper_parity_manifest.json` all keep `zigux/tests/phase6_base64_perf.zig` explicit beside the focused helper replay, shared vectors, and direct C parity packet. The next honest same-lane reopen is therefore narrower and adjacent to the helper-owned perf gate: either restore a committed `phase6-base64-perf` target body in `zigux/Makefile` or update the remaining shared route-inventory surfaces so they stop presenting that Linux-style wrapper as runnable current-`master` evidence before it exists.
