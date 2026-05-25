# Phase 6 Base64 Slice

This document records a bounded Phase 6 leaf-helper validation slice for Zigux.

## Status

- `PHASE6_STATUS=active`
- `PHASE6_SLICE=base64-leaf-helper`
- scope: first low-risk base64 helper coverage only
- product boundary:
  - `lib/base64.zig`
  - `zigux/tests/phase6_base64.zig`
  - `zigux/tests/phase6_base64_perf.zig`
  - `zigux/tests/fixtures/phase6_base64_vectors.zig`
  - `zigux/tests/phase6_base64_c_parity.zig`
  - `zigux/tests/fixtures/phase6_base64_c_harness.c`
  - `scripts/zigux/check-phase6-base64-c-parity.py`
- shared helper-evidence row:
  - `Documentation/zigux/phase6-helper-evidence-catalog.md`
  - `zigux/tests/phase6_helper_evidence_manifest.json`
  - `zigux/tests/phase6_helper_parity_manifest.json`

## Why this slice exists

Phase 6 is where Zigux can keep proving low-risk in-kernel helper ports without stepping into runtime-core or driver complexity.

`lib/base64.c` is a good next slice because it is:

- leaf-oriented
- small enough to validate with deterministic vectors
- a clean parity target for variant-sensitive helper behavior

## Gates

1. run the focused Zig Phase 6 helper tests
- local scratch validation in this run used a dedicated `zig build test` replay wired only to `lib/base64.zig`, `zigux/tests/phase6_base64.zig`, and `zigux/tests/fixtures/phase6_base64_vectors.zig`

2. keep the base64 slice note aligned with the shipped helper-local validation packet
- `Documentation/zigux/phase6-helper-evidence-catalog.md`, `zigux/tests/phase6_helper_evidence_manifest.json`, and `zigux/tests/phase6_helper_parity_manifest.json` should describe this slice as directly readable helper-local evidence plus the committed perf replay and the restored representative C-vs-Zig spot check in `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`

## Current parity surface

The current base64 helper surface exercised by this slice covers:

- generic `chars`, `paddedChars`, `unpaddedChars`, `bytes`, `encode`, and `decode`
- generic `encodeSlice`, `encodeAlloc`, `decodeSlice`, and `decodeAlloc`
- variant-pinned `bytesStd`, `bytesUrlsafe`, and `bytesImap`
- variant-pinned `encodeStd`, `encodeUrlsafe`, and `encodeImap`
- variant-pinned `encodeStdSlice`, `encodeUrlsafeSlice`, and `encodeImapSlice`
- variant-pinned `encodeStdAlloc`, `encodeUrlsafeAlloc`, and `encodeImapAlloc`
- variant-pinned `decodeStd`, `decodeUrlsafe`, and `decodeImap`
- variant-pinned `decodeStdSlice`, `decodeUrlsafeSlice`, and `decodeImapSlice`
- variant-pinned `decodeStdAlloc`, `decodeUrlsafeAlloc`, and `decodeImapAlloc`
- `Variant.std`
- `Variant.urlsafe`
- `Variant.imap`

The current tests check:

- standard RFC 4648 encode vectors with and without padding
- standard RFC 4648 decode vectors with and without padding
- variant alphabet parity for URL-safe and IMAP output
- variant alphabet parity for URL-safe and IMAP output with and without padding
- one-byte and two-byte std, URL-safe, and IMAP tail parity with and without padding
- output-length accounting through `chars`
- preflight decoded-length accounting through `bytes`
- helper-local direct checks for `chars`, `bytes`, convenience-wrapper foreign-alphabet rejection, and exact-fit encode/decode buffer boundaries across the bounded std, URL-safe, and IMAP fixture packet
- helper-local same-file sweeps for `paddedChars` and `unpaddedChars`
- helper-local convenience parity between the generic and variant-pinned size, direct, slice, and allocator encode/decode entrypoints
- destination-bounds failures before partial writes
- exact-fit encode and decode buffers across the shared standard and variant fixture surface, plus the matching convenience-wrapper exact-fit and one-byte-short boundary proofs for std, URL-safe, and IMAP encode/decode wrappers before writes
- shared kernel-derived encode, decode, and invalid-input fixtures stored in `zigux/tests/fixtures/phase6_base64_vectors.zig` and consumed directly by `zigux/tests/phase6_base64.zig`
- exact fixture-owned corpus counts on current `master`: 22 standard encode cases, 18 variant encode cases, 22 standard decode cases, 18 variant decode cases, 16 invalid decode cases, and 6 perf replay cases, all centralized in `zigux/tests/fixtures/phase6_base64_vectors.zig` and replayed by `zigux/tests/phase6_base64.zig` or `zigux/tests/phase6_base64_perf.zig`
- exact helper-local perf replay packet: ordered labels `STD_PAD`, `STD_NO_PAD`, `URLSAFE_PAD`, `URLSAFE_NO_PAD`, `IMAP_PAD`, and `IMAP_NO_PAD`, each with `iterations = 12000`, `max_encode_slowdown_pct = 150`, and `max_decode_slowdown_pct = 325`, owned once in `zigux/tests/fixtures/phase6_base64_vectors.zig` and replayed by the helper-local perf gate
- helper-local corpus checker: `scripts/zigux/check-phase6-base64-corpus-determinism.py`
- fixture-backed variant decode parity for std, URL-safe, and IMAP sample payloads, including one-byte and two-byte tails with and without padding
- invalid-input rejection for malformed, embedded-NUL, and variant-mismatched decode inputs
- extra kernel KUnit parity vectors for uppercase, lowercase, and digit-heavy standard cases
- the committed slowdown replay in `zigux/tests/phase6_base64_perf.zig`, which keeps the helper tied to the shared Phase 6 build foothold without widening into broader runtime-core work
- a representative external C-vs-Zig portability replay through `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`, covering standard padded and unpadded cases plus URL-safe, IMAP, and malformed decode spot checks
- the dedicated parity checker self-test contract in `scripts/zigux/check-phase6-base64-c-parity.py`, which still records `PHASE6_BASE64_C_PARITY_SELF_TEST_CASE_COUNT=5` separately from the broader replayed portability packet

## Non-goals

This slice does not yet claim:

- KUnit integration
- architecture-specific performance thresholds beyond the committed helper-local slowdown replay
- a broader generated external-fixture flow or shared manifest refresh for the restored direct C parity packet beyond the representative checker, runner, and harness now shipped in-tree

## Next bounded step

Leave this helper parked unless fresh repo inspection shows a concrete parity, portability, or helper-surface truthfulness drift in the current generic, variant-pinned, slice, alloc, exact-fit buffer, or representative C-vs-Zig parity packet. If the base64 family reopens, start by rerunning `zig build phase6-base64-test --build-file zigux/tests/phase6_build.zig` and `zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig`, or the matching `make -C zigux phase6-base64-test` and `make -C zigux phase6-base64-perf` wrappers, before any helper-local repair. Keep any follow-through to one small truthfulness step inside this slice note or one direct expansion of the restored parity spot check instead of widening into broader Phase 6 shared-note churn.
