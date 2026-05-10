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
- a direct 24-case C-vs-Zig spot check covering representative std, URL-safe, and IMAP encode parity, decoded-byte parity, returned encoded-size parity through `chars`, returned decoded-size parity through `bytes`, and malformed-tail rejection through `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`

## Next Step
Leave this slice parked unless helper behavior, direct C parity evidence, or the dedicated perf replay drifts on current `master`.
