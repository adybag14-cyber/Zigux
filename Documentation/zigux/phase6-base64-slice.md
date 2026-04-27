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
- output-length accounting through `chars`
- preflight decoded-length accounting through `bytes`
- destination-bounds failures before partial writes
- exact-fit encode and decode buffers across the shared standard and variant fixture surface, plus one-byte-short rejection before writes
- shared kernel-derived encode, decode, and invalid-input fixtures stored in `zigux/tests/fixtures/phase6_base64_vectors.zig` and consumed directly by `zigux/tests/phase6_base64.zig`
- invalid-input rejection for malformed, embedded-NUL, and variant-mismatched decode inputs
- extra kernel KUnit parity vectors for uppercase, lowercase, and digit-heavy standard cases
- a deterministic 64-byte and 1-kibibyte encode/decode timing harness that prints per-operation timings while rechecking round-trip correctness

## Non-goals

This slice does not yet claim:

- KUnit integration
- a hard performance threshold that would be too environment-sensitive for this early leaf-helper lane
- a C-emitted parity harness beyond the current Zig fixture module

## Next bounded step

Decide whether the helper now needs a small external C-vs-Zig fixture layer beyond the direct shared fixture module, or whether the current parity surface plus the reviewable performance-sanity step is already sufficient for this bounded Phase 6 leaf port.
