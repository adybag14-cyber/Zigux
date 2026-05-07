# Phase 6 Base64 Slice

This document records a bounded Phase 6 leaf-helper validation slice for Zigux.

## Status

- `PHASE6_STATUS=parked`
- `PHASE6_SLICE=base64-leaf-helper`
- scope: first low-risk base64 helper coverage only
- lane state: helper, fixture, perf, and external parity slice landed; parked unless a new `base64.c` parity or slowdown issue appears
- product boundary:
  - `lib/base64.zig`
  - `zigux/tests/phase6_base64.zig`
  - `zigux/tests/phase6_base64_perf.zig`
  - `zigux/tests/phase6_base64_c_parity.zig`
  - `zigux/tests/phase6_base64_c_casegen.zig`
  - `zigux/tests/fixtures/phase6_base64_vectors.zig`
  - `zigux/tests/fixtures/phase6_base64_c_harness.c`
  - `zigux/tests/phase6_build.zig`
  - `zigux/Makefile`
  - `scripts/zigux/check-phase6-base64-c-parity.py`

## Why this slice exists

Phase 6 is where Zigux can keep proving low-risk in-kernel helper ports without stepping into runtime-core or driver complexity.

`lib/base64.c` is a good next slice because it is:

- leaf-oriented
- small enough to validate with deterministic vectors
- a clean parity target for variant-sensitive helper behavior

## Gates

1. run the shared Phase 6 leaf-helper replay
- `zig build test --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6`

2. keep the shared Phase 6 surface checker aligned with this slice
- `make -C zigux phase6-validate`

3. keep the bounded external parity replay aligned with the helper-local packet
- `python3 scripts/zigux/check-phase6-base64-c-parity.py --self-test`
- `python3 scripts/zigux/check-phase6-base64-c-parity.py`

4. keep the dedicated base64 perf sanity replay green
- `zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig`

## Current parity surface

The current base64 helper surface exercised by this slice covers:

- `chars`
- `bytes`
- `encode`
- `decode`
- `Variant.std`
- `Variant.urlsafe`
- `Variant.imap`
- per-variant reverse lookup maps that mirror the kernel helper's decode classification shape for std, URL-safe, and IMAP inputs

The current tests check:

- standard RFC 4648 encode vectors with and without padding
- standard RFC 4648 decode vectors with and without padding
- fixture-backed decode-length parity through `bytes` across the full committed valid std, URL-safe, and IMAP decode corpus
- variant alphabet parity for URL-safe and IMAP output
- variant decode parity for URL-safe and IMAP inputs
- output-length accounting through `chars`
- destination-bounds failures before partial writes during both encode and decode
- shared kernel-derived encode, decode, variant, and invalid-input fixtures stored in `zigux/tests/fixtures/phase6_base64_vectors.zig`
- invalid-input rejection through both `bytes` and `decode` for malformed, embedded-NUL, and variant-mismatched decode inputs
- exhaustive canonical tail acceptance for padded and unpadded std, URL-safe, and IMAP decode paths
- dedicated encode and decode perf sanity across std and URL-safe paths with and without padding through `zigux/tests/phase6_base64_perf.zig`
- IMAP remains covered by functional parity and decode-classification checks, not by the dedicated perf gate
- the bounded external C-vs-Zig replay packet through `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/phase6_base64_c_casegen.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `python3 scripts/zigux/check-phase6-base64-c-parity.py`, including the current `PHASE6_BASE64_C_PARITY_SELF_TEST_CASE_COUNT=10` review gate and `PHASE6_BASE64_C_PARITY_CASES=122` spot check

## Non-goals

This slice does not yet claim:

- KUnit integration
- committed generated fixture artifacts on `master`
- broader runtime-core or driver-facing expansion beyond the shipped helper, perf, and external parity packet

## Next bounded step

Keep the next Phase 6 follow-up inside the shared bundled `base64`, `bsearch`, `checksum`, and `hexdump` packet already gated by `zigux/tests/phase6_build.zig`, `zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig`, `make -C zigux phase6`, and `make -C zigux phase6-validate`. Reopen this slice only if fresh repo inspection finds a concrete new `base64.c` parity or slowdown gap inside `lib/base64.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_base64_perf.zig`, the committed fixture corpus, or the existing external parity packet.