# Phase 6 Base64 Slice

This document records a bounded Phase 6 leaf-helper validation slice for Zigux.

## Status

- `PHASE6_STATUS=parked`
- `PHASE6_SLICE=base64-leaf-helper`
- scope: first low-risk base64 helper coverage only
- lane state: helper, perf, and representative external-parity slice landed; parked unless a new `base64.c` parity issue appears
- product boundary:
  - `lib/base64.zig`
  - `zigux/tests/phase6_base64.zig`
  - `zigux/tests/phase6_base64_perf.zig`
  - `zigux/tests/phase6_base64_c_parity.zig`
  - `zigux/tests/phase6_base64_c_casegen.zig`
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

1. run the focused Zig Phase 6 helper tests
- `zig build test --build-file zigux/tests/phase6_build.zig`

2. keep the helper wired through the Zigux convenience target
- `make -C zigux phase6`

3. keep the helper-local perf replay reviewable
- `make -C zigux phase6-base64-perf`

4. keep the representative external C-vs-Zig parity replay aligned
- `python3 scripts/zigux/check-phase6-base64-c-parity.py --self-test`
- `python3 scripts/zigux/check-phase6-base64-c-parity.py`

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
- exhaustive canonical tail acceptance for padded and unpadded std, URL-safe, and IMAP decode paths
- two deterministic perf payload replays covering `64B` and `1KB` inputs with the current encode and decode slowdown ceilings
- a generated representative external C-vs-Zig parity replay that rebuilds transient cases from the committed fixture corpus before the current `PHASE6_BASE64_C_PARITY_CASES=122` spot check runs

## Non-goals

This slice does not yet claim:

- KUnit integration
- a fully exhaustive emitted external parity corpus beyond the current representative generated replay
- broader runtime-core or driver-facing expansion

## Next bounded step

Keep the next Phase 6 follow-up inside the shared bundled `base64`, `bsearch`, `checksum`, and `hexdump` packet already gated by `zigux/tests/phase6_build.zig`, `make -C zigux phase6`, `make -C zigux phase6-base64-perf`, and `python3 scripts/zigux/check-phase6-base64-c-parity.py`. Reopen this slice only if fresh repo inspection finds a concrete new `base64.c` parity gap inside `lib/base64.zig`, `zigux/tests/phase6_base64.zig`, the committed fixture corpus, the perf replay, or the representative external parity gate.