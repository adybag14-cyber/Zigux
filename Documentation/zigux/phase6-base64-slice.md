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
  - `zigux/tests/phase6_build.zig`
  - `zigux/Makefile`

## Why this slice exists

Phase 6 is where Zigux can keep proving low-risk in-kernel helper ports without stepping into runtime-core or driver complexity.

`lib/base64.c` is a good next slice because it is:

- leaf-oriented
- small enough to validate with deterministic vectors
- a clean parity target for variant-sensitive helper behavior

## Gates

1. run the focused Zig Phase 6 helper tests
- `zig build test --build-file zigux/tests/phase6_build.zig`

2. keep the helper wired through the Zigux convenience target
- `make -C zigux phase6`

3. run the narrow performance sanity harness when reviewing math-sensitive helper drift
- `zig build base64-perf --build-file zigux/tests/phase6_build.zig`
- or `make -C zigux phase6-base64-perf`

4. run the external C-vs-Zig parity spot check when reviewing portability-sensitive helper drift
- `python3 scripts/zigux/check-phase6-base64-c-parity.py`

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
- a small external C-vs-Zig spot-check harness that compiles `zigux/tests/fixtures/phase6_base64_c_harness.c`, runs it beside `zigux/tests/phase6_base64_c_parity.zig`, and compares representative encode, decode, decoded-length preflight, and invalid-input cases with explicit coverage for no-padding one-byte and two-byte tails plus malformed decode inputs
- invalid-input rejection for malformed, embedded-NUL, and variant-mismatched decode inputs
- exhaustive reverse-map classification across all 256 byte values for the standard, URL-safe, and IMAP decode variants
- extra kernel KUnit parity vectors for uppercase, lowercase, and digit-heavy standard cases
- a deterministic 64-byte and 1-kibibyte encode/decode timing harness that compares the helper against the padded `std.base64.standard` reference path and rejects regressions beyond the current fixture-backed encode and decode slowdown budgets while rechecking round-trip correctness

## Non-goals

This slice does not yet claim:

- KUnit integration
- variant-wide or architecture-specific performance thresholds beyond the current padded standard-path slowdown gate
- a full generated external fixture corpus beyond the current representative C-vs-Zig spot-check harness

## Next bounded step

Leave this helper parked unless fresh repo inspection shows a concrete parity or padded-standard perf drift. If Phase 6 base64 reopens, keep the next step narrow: either widen the representative external C-vs-Zig corpus into a generated fixture flow, extend the same slowdown-gate discipline to another clearly justified variant path, or retire the current spot check if a better shared parity substrate replaces it.
