# Phase 6 Base64 Slice

This document records a bounded Phase 6 leaf-helper validation slice for Zigux.

## Status

- `PHASE6_STATUS=active`
- `PHASE6_SLICE=base64-leaf-helper`
- scope: first low-risk base64 helper coverage only
- product boundary:
  - `lib/base64.zig`
  - `zigux/tests/phase6_base64.zig`
  - `zigux/tests/fixtures/phase6_base64_vectors.zig`

## Why this slice exists

Phase 6 is where Zigux can keep proving low-risk in-kernel helper ports without stepping into runtime-core or driver complexity.

`lib/base64.c` is a good next slice because it is:

- leaf-oriented
- small enough to validate with deterministic vectors
- a clean parity target for variant-sensitive helper behavior

## Gates

1. run the focused Zig Phase 6 helper tests
- local scratch validation in this run used a dedicated `zig build test` replay wired only to `lib/base64.zig`, `zigux/tests/phase6_base64.zig`, and `zigux/tests/fixtures/phase6_base64_vectors.zig`

## Current parity surface

The current base64 helper surface exercised by this slice covers:

- `chars`
- `bytes`
- `encode`
- `decode`
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
- destination-bounds failures before partial writes
- exact-fit encode and decode buffers across the shared standard and variant fixture surface, plus one-byte-short rejection before writes
- shared kernel-derived encode, decode, and invalid-input fixtures stored in `zigux/tests/fixtures/phase6_base64_vectors.zig` and consumed directly by `zigux/tests/phase6_base64.zig`
- invalid-input rejection for malformed, embedded-NUL, and variant-mismatched decode inputs
- exhaustive reverse-map classification across all 256 byte values for the standard, URL-safe, and IMAP decode variants
- extra kernel KUnit parity vectors for uppercase, lowercase, and digit-heavy standard cases

## Non-goals

This slice does not yet claim:

- KUnit integration
- architecture-specific performance thresholds
- a generated external C-vs-Zig parity packet on current `master`

## Next bounded step

Leave this helper parked unless fresh repo inspection shows a concrete parity or portability drift in the current standard, URL-safe, or IMAP packet. The focused Phase 6 build-root and perf packet are already present on current `master`; the only still-missing same-helper companion visible from this note is the direct C-vs-Zig parity packet, so any reopen should stay there rather than broad shared-note churn.
