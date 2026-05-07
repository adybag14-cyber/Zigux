# Phase 6 Checksum Slice

This document starts a bounded Phase 6 leaf-helper port for Zigux.

## Status

- `PHASE6_STATUS=parked`
- `PHASE6_SLICE=checksum-leaf-helper`
- scope: first low-risk checksum helper only
- lane state: helper, fixture, perf, and direct C parity slice landed; parked unless a new `checksum.c` parity issue appears
- product boundary:
  - `lib/checksum.zig`
  - `zigux/tests/phase6_checksum.zig`
  - `zigux/tests/phase6_checksum_c_parity.zig`
  - `zigux/tests/phase6_checksum_perf.zig`
  - `zigux/tests/fixtures/phase6_checksum_vectors.zig`
  - `zigux/tests/fixtures/phase6_checksum_c_harness.c`
  - `scripts/zigux/check-phase6-checksum-c-parity.py`
  - `zigux/tests/phase6_build.zig`
  - `zigux/Makefile`

## Why this slice exists

Phase 6 is where Zigux can start proving low-risk in-kernel helper ports without stepping into runtime-core or driver complexity.

`lib/checksum.c` is a good first slice because it is:

- leaf-oriented
- math-sensitive enough to justify a focused gate
- small enough to validate without inventing a broad new subsystem

## Gates

1. run the shared Phase 6 leaf-helper replay
- `zig build test --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6`

2. run the dedicated checksum C parity replay when portability-sensitive behavior moves
- `python3 scripts/zigux/check-phase6-checksum-c-parity.py --self-test`
- `ZIG=zig python3 scripts/zigux/check-phase6-checksum-c-parity.py`

3. run the dedicated checksum perf gate when the math-sensitive lane reopens
- `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe`
- `make -C zigux phase6-checksum-perf`

4. keep the shared Phase 6 surface checker aligned with this slice
- `make -C zigux phase6-validate`

## Current parity surface

The current checksum helper surface exercised by this slice covers:

- `add`
- `sub`
- `shift`
- `blockAdd`
- `blockSub`
- `negate`
- `replace`
- `replaceByDiff`
- `replace2`
- `replace4`
- `from32to16`
- `fold`
- `unfold`
- `add16`
- `sub16`
- `tcpUdpNofold`
- `tcpUdpV6Nofold`
- `partial`
- `compute`
- `ipFastCsum`

The current tests check:

- fixture-backed checksum vectors for empty, even, odd, and carry-heavy inputs
- explicit IPv4 fast-header parity through `ipFastCsum` over the fixture-backed 20-byte header case
- incremental partial-sum chaining across even and odd fragment boundaries
- non-zero seeded `partial` accumulation parity across odd, carry-heavy, and pre-folded seed inputs
- fixture-backed carry-discipline and imported KUnit random-prefix replays for all-ones prefixes and no-spurious-carry seeded cases
- fixture-backed fold reviewability for `from32to16` and `fold`
- direct stored-checksum word exposure through `unfold` stays explicit for replacement-helper reviewability
- IPv4 and IPv6 pseudo-header accumulation parity between the dedicated helper paths and manual `partial` plus `blockAdd` composition
- incremental checksum replacement parity for payload word updates, 16-bit IPv4 header field replacement, diff-based checksum repair, and 32-bit IPv4 address replacement
- a direct 30-case C-vs-Zig replay for compute, seeded partial, composition, IPv4 and IPv6 pseudo-header, direct `negate`, direct `from32to16` and `fold`, and incremental replacement behavior
- helper-local wraparound, double-negation, and one's-complement carry checks for `negate`
- helper-local perf smoke on patterned 64-byte and 1501-byte payloads keeps `checksum.compute` within a 150% slowdown ceiling versus the bounded reference loop
- the live perf fixture matrix keeps `64B` at `iterations = 200_000` and `1501B` at `iterations = 12_000`, with `max_slowdown_pct = 150` for both cases

The fixture layer stays intentionally small. It names representative Phase 6 parity cases in one place, borrows a small carry-discipline shape from `lib/tests/checksum_kunit.c` without claiming a full KUnit surface port, and now pairs that fixture corpus with a direct external C replay so reviewable parity does not stop at Zig-only expectations.

## Non-goals

This slice does not yet claim:

- arch-specific assembly fast paths
- kbuild integration into the kernel proper
- performance equivalence across all architectures

## Next bounded step

Keep the next Phase 6 follow-up inside the shared bundled `base64`, `bsearch`, `checksum`, and `hexdump` packet already gated by `zigux/tests/phase6_build.zig` and `make -C zigux phase6`. Reopen this slice only if fresh repo inspection finds a concrete new `checksum.c` parity gap inside `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_c_parity.zig`, `scripts/zigux/check-phase6-checksum-c-parity.py`, `zigux/tests/phase6_checksum_perf.zig`, the shared fixture module, or that existing bundled gate.
