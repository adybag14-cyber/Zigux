# Phase 6 Base64 Slice

This document starts a bounded Phase 6 leaf-helper validation slice for Zigux.

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

## Current parity surface

The current base64 helper surface exercised by this slice covers:

- `chars`
- `encode`
- `Variant.std`
- `Variant.urlsafe`
- `Variant.imap`

The current tests check:

- standard RFC 4648 encode vectors with and without padding
- variant alphabet parity for URL-safe and IMAP output
- output-length accounting through `chars`
- destination-bounds failures before partial writes
- shared encode fixtures stored in `zigux/tests/fixtures/phase6_base64_vectors.zig`

## Non-goals

This slice does not yet claim:

- decode parity
- KUnit integration
- performance benchmarking
- a C-emitted parity harness beyond the current Zig fixture module

## Next bounded step

Add `decode` with focused valid-and-invalid parity vectors lifted from `lib/tests/base64_kunit.c`, then decide whether the helper needs a small external C-vs-Zig fixture layer or is ready to be left as a bounded Phase 6 leaf port.
