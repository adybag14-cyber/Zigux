# Phase 6 Base64 Slice

This document records a bounded Phase 6 leaf-helper validation slice for Zigux.

## Status

- `PHASE6_STATUS=parked`
- `PHASE6_SLICE=base64-leaf-helper`
- scope: first low-risk base64 helper coverage only
- lane state: helper, fixture, dedicated perf, and direct C parity spot-check slices landed; parked unless a new helper-local parity or slowdown issue appears
- product boundary:
  - `lib/base64.zig`
  - `zigux/tests/phase6_base64.zig`
  - `zigux/tests/phase6_base64_c_parity.zig`
  - `zigux/tests/phase6_base64_perf.zig`
  - `zigux/tests/fixtures/phase6_base64_vectors.zig`
  - `zigux/tests/fixtures/phase6_base64_c_harness.c`
  - `scripts/zigux/check-phase6-base64-c-parity.py`
  - `zigux/tests/phase6_build.zig`
  - `zigux/Makefile`

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

2. run the dedicated base64 C parity replay when portability-sensitive behavior moves
- `python3 scripts/zigux/check-phase6-base64-c-parity.py --self-test`
- `ZIG=zig python3 scripts/zigux/check-phase6-base64-c-parity.py`

3. keep the exact base64 fixture-corpus evidence aligned
- `python3 scripts/zigux/check-phase6-base64-fixture-evidence.py --self-test`
- `python3 scripts/zigux/check-phase6-base64-fixture-evidence.py`

4. keep the shared Phase 6 surface checker aligned with this slice
- `make -C zigux phase6-validate`

5. keep the dedicated base64 perf sanity replay green
- `zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6-base64-perf`

## Current parity surface

The current base64 helper surface exercised by this slice covers:

- `paddedChars`
- `chars`
- `bytes`
- `maxDecodedBytes`
- `encode`
- `decode`
- `Variant.std`
- `Variant.urlsafe`
- `Variant.imap`
- per-variant reverse lookup maps that mirror the kernel helper's decode classification shape for std, URL-safe, and IMAP inputs
- helper-local canonical tail validation for padded and unpadded std, URL-safe, and IMAP decode paths

The current landed helper and replay tests check:

- standard RFC 4648 encode vectors with and without padding
- standard RFC 4648 decode vectors with and without padding
- fixture-backed decode-length parity through `bytes` across the full committed valid std, URL-safe, and IMAP decode corpus
- variant alphabet parity for URL-safe and IMAP output
- variant decode parity for URL-safe and IMAP inputs
- output-length accounting through `paddedChars`, `chars`, and `maxDecodedBytes`
- exact-fit encode and decode buffers across std, URL-safe, and IMAP inputs
- empty encode and decode inputs stay zero-length no-ops across std, URL-safe, and IMAP variants
- destination-bounds failures before partial writes during both encode and decode
- shared kernel-derived encode, decode, variant, invalid-input, and dedicated perf-corpus fixtures stored in `zigux/tests/fixtures/phase6_base64_vectors.zig`
- invalid-input rejection through both `bytes` and `decode` for malformed, embedded-NUL, and variant-mismatched decode inputs
- decode success keeps caller bytes past the returned payload untouched, and invalid-input rejection keeps destination bytes untouched
- exhaustive canonical tail acceptance for padded and unpadded std, URL-safe, and IMAP decode paths
- exhaustive one-byte and two-byte roundtrip coverage across std, URL-safe, and IMAP variants with and without padding
- dedicated encode and decode perf sanity across std and URL-safe paths with and without padding through `zigux/tests/phase6_base64_perf.zig`, which consumes the same committed four-case perf corpus and payload markers from `zigux/tests/fixtures/phase6_base64_vectors.zig`
- a direct 24-case C-vs-Zig spot check derived from the same committed standard, variant, and malformed-tail expectations in `zigux/tests/fixtures/phase6_base64_vectors.zig`, covering representative std, URL-safe, and IMAP encode parity, decoded-byte parity, returned encoded-size parity through `chars`, returned decoded-size parity through `bytes`, and malformed-tail rejection through `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`

The fixture layer stays intentionally small. It keeps the deterministic parity matrix and the committed four-case slowdown corpus reviewable in one place, and the direct C replay now reads those same committed vector expectations through `zigux/tests/phase6_base64_c_parity.zig` before checking them against the C harness, so portability-sensitive behavior does not stop at Zig-only expectations. The manifest-backed fixture counts and perf-payload marker now stay fail-closed through `scripts/zigux/check-phase6-base64-fixture-evidence.py` as well.

## Non-goals

This slice does not yet claim:

- KUnit integration
- committed generated fixture artifacts on `master`
- broader runtime-core or driver-facing expansion beyond the shipped helper, fixture, direct parity, and dedicated perf packet

## Next bounded step

Keep the next Phase 6 follow-up inside the shared bundled `base64`, `bsearch`, `checksum`, and `hexdump` packet already gated by `zigux/tests/phase6_build.zig`, `zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig`, `make -C zigux phase6`, `make -C zigux phase6-base64-perf`, and `make -C zigux phase6-validate`. Reopen this slice only if fresh repo inspection finds a concrete new helper-local parity or slowdown gap inside `lib/base64.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/phase6_base64_perf.zig`, `scripts/zigux/check-phase6-base64-c-parity.py`, or the committed fixture corpus.
