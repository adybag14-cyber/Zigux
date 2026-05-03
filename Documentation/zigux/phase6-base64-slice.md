# Phase 6 Base64 Slice

This document records a bounded Phase 6 leaf-helper validation slice for Zigux.

## Status

- `PHASE6_STATUS=active`
- `PHASE6_SLICE=base64-leaf-helper`
- scope: first low-risk base64 helper coverage only
- lane posture: parked after the current parity surface cleared the bounded helper goal
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

1. run the shared Phase 6 validator-first handoff before helper-local replay
- `python3 scripts/zigux/validate-phase6.py --self-test`
- `make -C zigux phase6-validate`

2. run the focused Zig Phase 6 helper tests
- `zig build test --build-file zigux/tests/phase6_build.zig`

3. keep the helper wired through the Zigux convenience target
- `make -C zigux phase6`

4. run the narrow performance sanity harness when reviewing math-sensitive helper drift
- `zig build base64-perf --build-file zigux/tests/phase6_build.zig`
- or `make -C zigux phase6-base64-perf`

5. run the external C-vs-Zig parity spot check when reviewing portability-sensitive helper drift
- `python3 scripts/zigux/check-phase6-base64-c-parity.py`
- `python3 scripts/zigux/check-phase6-base64-c-parity.py --self-test`

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
- shared kernel-derived encode, decode, and invalid-input fixtures stored in `zigux/tests/fixtures/phase6_base64_vectors.zig` and consumed directly by `zigux/tests/phase6_base64.zig`, including two repeated-alternate-alphabet multi-quartet sample families for the URL-safe and IMAP branches: one five-byte packet and one seven-byte replay that exercises repeated alternate-alphabet quartets plus a one-byte tail
- the same `zigux/tests/fixtures/phase6_base64_vectors.zig` module now owns both the deterministic 64-byte and 1-kibibyte perf payload corpus and the shipped ten-case padded and unpadded standard, URL-safe, and IMAP perf replay matrix that `zigux/tests/phase6_base64_perf.zig` consumes directly
- a small external C-vs-Zig spot-check harness that now also carries a built-in ten-case `--self-test` path for its missing-path guards, generated build template, sorted-output normalization, representative-output fail-closed drift checks, and explicit C-versus-Zig `c_output_mismatch` handling before it regenerates the transient `zigux/tests/fixtures/phase6_base64_c_generated_cases.inc` include payload through `zigux/tests/phase6_base64_c_casegen.zig`, compiles `zigux/tests/fixtures/phase6_base64_c_harness.c`, runs it beside `zigux/tests/phase6_base64_c_parity.zig`, and compares representative encode, decode, decoded-length preflight, and invalid-input cases with explicit coverage for padded and no-padding one-byte and two-byte tail replays plus malformed decode inputs, including padded malformed tail-bit rejects across the standard, URL-safe, and IMAP variants
- invalid-input rejection for malformed, embedded-NUL, variant-mismatched, and padded plus unpadded non-canonical tail-bit decode inputs through the shared fixture packet and the external C-vs-Zig spot check
- exhaustive reverse-map classification across all 256 byte values for the standard, URL-safe, and IMAP decode variants
- extra kernel KUnit parity vectors for uppercase, lowercase, and digit-heavy standard cases
- a deterministic base64 perf harness that now consumes the shared fixture module's payload and replay-matrix tables, compares the helper against the padded `std.base64.standard` reference path, the padded and unpadded `std.base64.url_safe{,_no_pad}` reference paths, and translated padded plus unpadded IMAP reference paths, and rejects regressions beyond the current fixture-backed encode and decode slowdown budgets using a median-of-three slowdown sample while rechecking round-trip correctness

This is enough evidence to leave the bounded base64 helper lane parked unless a concrete new parity, perf, or directly coupled review-packet gap appears in the live repo.

## Non-goals

This slice does not yet claim:

- KUnit integration
- architecture-specific performance thresholds beyond the current padded standard-path plus padded and unpadded URL-safe and IMAP slowdown gates
- a full generated external fixture corpus beyond the current representative C-vs-Zig spot-check harness

## Next bounded step

Leave the base64 helper lane parked unless fresh repo inspection finds a concrete parity, perf, or directly coupled review-packet gap inside `lib/base64.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_base64_perf.zig`, `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/phase6_base64_c_casegen.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, `scripts/zigux/check-phase6-base64-c-parity.py`, or the shared Phase 6 packet. If reviewers want the shared packet to enumerate the current base64 evidence more explicitly, the next same-family follow-up should stay narrow to `Documentation/zigux/phase6-helper-parity-catalog.md`, `zigux/tests/phase6_helper_parity_manifest.json`, and any directly coupled validator markers so those shared surfaces also acknowledge the live base64 perf and external parity packet more directly.
