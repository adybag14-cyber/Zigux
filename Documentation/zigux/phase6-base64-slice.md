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
- `zigux/tests/fixtures/phase6_base64_vectors.zig` owns the current slowdown corpus boundary through `perfReferenceSupportedVariant()`, so the shipped perf packet is intentionally limited to the direct `std` and `urlsafe` baselines until an explicit IMAP slowdown baseline lands
- the same fixture packet now carries a helper drift guard that exact-checks `lib/base64.zig`'s public sizing, encode, decode, and invalid-input surface against the committed standard, variant, and perf-backed vectors before the dedicated perf replay runs

## Next Step
Leave this slice parked unless helper behavior, focused fixture-backed replay coverage, or the dedicated perf replay drifts on current `master`.
