# Phase 6 Base64 Slice

This document records a bounded Phase 6 leaf-helper validation slice for Zigux.

## Status

- `PHASE6_STATUS=parked`
- `PHASE6_SLICE=base64-leaf-helper`
- scope: first low-risk base64 helper coverage only
- lane state: helper and fixture slice landed; parked unless a new `base64.c` parity issue appears
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
- `decode`
- `Variant.std`
- `Variant.urlsafe`
- `Variant.imap`

The current tests check:

- standard RFC 4648 encode vectors with and without padding
- standard RFC 4648 decode vectors with and without padding
- variant alphabet parity for URL-safe and IMAP output
- output-length accounting through `chars`
- destination-bounds failures before partial writes
- shared kernel-derived encode, decode, and invalid-input fixtures stored in `zigux/tests/fixtures/phase6_base64_vectors.zig`
- invalid-input rejection for malformed, embedded-NUL, and variant-mismatched decode inputs
- extra kernel KUnit parity vectors for uppercase, lowercase, and digit-heavy standard cases

## Non-goals

This slice does not yet claim:

- KUnit integration
- performance benchmarking
- a C-emitted parity harness beyond the current Zig fixture module

## Next bounded step

Keep the next Phase 6 follow-up inside the shared bundled `base64`, `bsearch`, `checksum`, and `hexdump` packet already gated by `zigux/tests/phase6_build.zig` and `make -C zigux phase6`. Reopen this slice only if fresh repo inspection finds a concrete new `base64.c` parity gap inside `lib/base64.zig`, `zigux/tests/phase6_base64.zig`, the shared fixture module, or that existing bundled gate.
