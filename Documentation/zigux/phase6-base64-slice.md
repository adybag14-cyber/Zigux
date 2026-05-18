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
- shared helper-evidence row:
  - `Documentation/zigux/phase6-helper-evidence-catalog.md`
  - `zigux/tests/phase6_helper_evidence_manifest.json`

## Why this slice exists

Phase 6 is where Zigux can keep proving low-risk in-kernel helper ports without stepping into runtime-core or driver complexity.

`lib/base64.c` is a good next slice because it is:

- leaf-oriented
- small enough to validate with deterministic vectors
- a clean parity target for variant-sensitive helper behavior

## Gates

1. run the focused Zig Phase 6 helper tests
- local scratch validation in this run used a dedicated `zig build test` replay wired only to `lib/base64.zig`, `zigux/tests/phase6_base64.zig`, and `zigux/tests/fixtures/phase6_base64_vectors.zig`

2. keep the base64 slice note aligned with the shared helper-evidence packet
- `Documentation/zigux/phase6-helper-evidence-catalog.md` and `zigux/tests/phase6_helper_evidence_manifest.json` should describe this slice as directly readable helper-local evidence plus the committed perf replay, while the older direct C parity companions remain a fresh-read follow-up rather than current shipped direct evidence

## Current parity surface

The current base64 helper surface exercised by this slice covers:

- generic `chars`, `bytes`, `encode`, and `decode`
- variant-pinned `bytesStd`, `bytesUrlsafe`, and `bytesImap`
- variant-pinned `encodeStd`, `encodeUrlsafe`, and `encodeImap`
- variant-pinned `decodeStd`, `decodeUrlsafe`, and `decodeImap`
- `Variant.std`
- `Variant.urlsafe`
- `Variant.imap`

The current tests check:

- standard RFC 4648 encode vectors with and without padding
- standard RFC 4648 decode vectors with and without padding
- variant alphabet parity for URL-safe and IMAP output
- variant alphabet parity for URL-safe and IMAP output with and without padding
- one-byte and two-byte URL-safe and IMAP tail parity with and without padding
- output-length accounting through `chars`
- preflight decoded-length accounting through `bytes`
- helper-local convenience parity between the generic and variant-pinned size, encode, and decode entrypoints
- destination-bounds failures before partial writes
- exact-fit encode and decode buffers across the shared standard and variant fixture surface, plus one-byte-short rejection before writes
- shared kernel-derived encode, decode, and invalid-input fixtures stored in `zigux/tests/fixtures/phase6_base64_vectors.zig` and consumed directly by `zigux/tests/phase6_base64.zig`
- exact fixture-owned corpus counts on current `master`: 22 standard encode cases, 18 variant encode cases, 22 standard decode cases, 12 variant decode cases, 16 invalid decode cases, and 6 perf replay cases, all centralized in `zigux/tests/fixtures/phase6_base64_vectors.zig` and replayed by `zigux/tests/phase6_base64.zig` or `zigux/tests/phase6_base64_perf.zig`
- fixture-backed variant decode parity for URL-safe and IMAP sample payloads, including one-byte and two-byte tails with and without padding
- invalid-input rejection for malformed, embedded-NUL, and variant-mismatched decode inputs
- extra kernel KUnit parity vectors for uppercase, lowercase, and digit-heavy standard cases
- the committed slowdown replay in `zigux/tests/phase6_base64_perf.zig`, which keeps the helper tied to the shared Phase 6 build foothold without widening into broader runtime-core work

## Non-goals

This slice does not yet claim:

- KUnit integration
- architecture-specific performance thresholds beyond the committed helper-local slowdown replay
- the older direct C-vs-Zig parity companions as current shipped direct evidence before fresh direct reads recover `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/phase6_base64_c_casegen.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`

## Next bounded step

Leave this helper parked unless fresh repo inspection shows a concrete parity, portability, or helper-surface truthfulness drift in the current generic, variant-pinned, or exact-fit buffer packet. If the base64 family reopens for review-surface follow-through, keep it to one small truthfulness step inside this slice note or to one fresh direct-read recovery pass for the direct C parity companions, instead of widening into broader Phase 6 shared-note churn.