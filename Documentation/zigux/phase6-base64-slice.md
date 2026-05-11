# Phase 6 Base64 Slice

## Status
- `PHASE6_STATUS=parked`
- `PHASE6_SLICE=base64-leaf-helper`
- helper anchor: `lib/base64.zig`
- shared packet note: `Documentation/zigux/phase6-helper-parity-catalog.md`

## Review Surface
- `zigux/tests/phase6_base64.zig`
- `zigux/tests/phase6_base64_perf.zig`
- `zigux/tests/fixtures/phase6_base64_vectors.zig`
- `zigux/tests/phase6_build.zig`
- `zigux/Makefile`
- `make -C zigux phase6-base64-perf`
- the focused helper replay keeps the shipped base64 packet reviewable through the committed standard, variant, decode, invalid-input, and variant-decode fixture loops in `zigux/tests/phase6_base64.zig`
- the dedicated base64 slowdown gate stays helper-local through `zigux/tests/phase6_base64_perf.zig` and `make -C zigux phase6-base64-perf`

## Next Step
Leave this slice parked unless helper behavior, focused fixture-backed replay coverage, or the dedicated perf replay drifts on current `master`.
