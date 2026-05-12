# Phase 6 Base64 Slice

## Status
- `PHASE6_STATUS=parked`
- `PHASE6_SLICE=base64-leaf-helper`
- helper anchor: `lib/base64.zig`
- shared packet note: `Documentation/zigux/phase6-helper-parity-catalog.md`

## Review Surface
- `zigux/tests/phase6_base64.zig`
- `zigux/tests/phase6_base64_c_parity.zig`
- `zigux/tests/phase6_base64_perf.zig`
- `zigux/tests/fixtures/phase6_base64_vectors.zig`
- `zigux/tests/fixtures/phase6_base64_c_harness.c`
- `scripts/zigux/check-phase6-base64-c-parity.py`
- `zigux/tests/phase6_build.zig`
- `zigux/Makefile`
- direct local C parity checker route: `python3 scripts/zigux/check-phase6-base64-c-parity.py`
- built-in parity-script self-test route: `python3 scripts/zigux/check-phase6-base64-c-parity.py --self-test`
- Linux-style C parity rerun route: `make -C zigux phase6-base64-c-parity`
- `make -C zigux phase6-base64-perf`
- the focused helper replay keeps the shipped base64 packet reviewable through the committed standard, variant, decode, invalid-input, and variant-decode fixture loops in `zigux/tests/phase6_base64.zig`
- a direct 24-case C-vs-Zig spot check covering representative std, URL-safe, and IMAP encode parity, decoded-byte parity, returned encoded-size parity through `chars`, returned decoded-size parity through `bytes`, and malformed-tail rejection through `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`
- the shipped parity script also keeps a built-in ten-case self-test for missing-path handling, fixture-surface parsing, unexpected or missing case detection, and explicit `c_output_mismatch` reporting before the live C-vs-Zig replay runs
- the checker-generated `zigux/tests/fixtures/phase6_base64_c_generated_cases.inc` include remains transient parity-run output from `zigux/tests/phase6_base64_c_casegen.zig` instead of a committed fixture, so the shipped direct C parity surface stays repo-truthful without storing generated case files on `master`
- the dedicated base64 slowdown gate stays helper-local through `zigux/tests/phase6_base64_perf.zig` and `make -C zigux phase6-base64-perf`
- `zigux/tests/fixtures/phase6_base64_vectors.zig` owns the current slowdown corpus boundary through `perfReferenceSupportedVariant()`, so the shipped perf packet is intentionally limited to the direct `std` and `urlsafe` baselines until an explicit IMAP slowdown baseline lands
- the same fixture packet now carries a helper drift guard that exact-checks `lib/base64.zig`'s public sizing, encode, decode, and invalid-input surface against the committed standard, variant, and perf-backed vectors before the dedicated perf replay runs

## Next Step
Leave this slice parked unless helper behavior, direct C parity evidence, focused fixture-backed replay coverage, or the dedicated perf replay drifts on current `master`.
