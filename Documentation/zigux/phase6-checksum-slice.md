# Phase 6 Checksum Slice

This document records the bounded Phase 6 leaf-helper validation slice for Zigux.

## Status

- `PHASE6_STATUS=parked`
- `PHASE6_SLICE=checksum-leaf-helper`
- scope: first low-risk checksum helper coverage only
- lane posture: parked after the current parity surface cleared the bounded helper goal
- product boundary:
  - `lib/checksum.zig`
  - `zigux/tests/phase6_checksum.zig`
  - `zigux/tests/phase6_checksum_perf.zig`
  - `zigux/tests/fixtures/phase6_checksum_vectors.zig`
  - `zigux/tests/phase6_checksum_c_parity.zig`
  - `zigux/tests/fixtures/phase6_checksum_c_harness.c`
  - `scripts/zigux/check-phase6-checksum-c-parity.py`
  - `zigux/tests/phase6_build.zig`
  - `zigux/Makefile`

## Why this slice exists

Phase 6 is where Zigux can keep proving low-risk in-kernel helper ports without stepping into runtime-core or driver complexity.

`lib/checksum.c` is a good Phase 6 slice because it is:

- leaf-oriented
- math-sensitive enough to justify a focused gate
- small enough to validate without inventing a broad new subsystem
- already ported with a committed helper, shared fixture corpus, focused external C-vs-Zig parity replay, and perf-sanity harness

## Gates

1. run the shared Phase 6 validator-first handoff before helper-local replay
- `python3 scripts/zigux/validate-phase6.py --self-test`
- `make -C zigux phase6-validate`

2. run the external checksum C-vs-Zig review hook when touching helper semantics
- `python3 scripts/zigux/check-phase6-checksum-c-parity.py --self-test`
- `python3 scripts/zigux/check-phase6-checksum-c-parity.py`

3. run the shared checksum-plus-hexdump perf-marker guard when touching perf reporting, thresholds, or reference-path wording
- `python3 scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py --self-test`
- `python3 scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py`

4. run the focused Zig Phase 6 helper tests
- `zig build test --build-file zigux/tests/phase6_build.zig`

5. keep the helper wired through the Zigux convenience target
- `make -C zigux phase6`

6. replay the checksum perf sanity harness when reviewing checksum-cost drift
- `zig build checksum-perf --build-file zigux/tests/phase6_build.zig`
- or `make -C zigux phase6-checksum-perf`

## Current parity surface

The current checksum helper surface exercised by this slice covers:

- `add`
- `sub`
- `negate`
- `shift`
- `blockAdd`
- `blockSub`
- `from32to16`
- `fold`
- `unfold`
- `add16`
- `sub16`
- `replaceByDiff`
- `replace4`
- `replace2`
- `replace`
- `tcpUdpNofold`
- `tcpUdpV6Nofold`
- `partial`
- `compute`

The current tests check:

- fixture-backed whole-buffer compute parity across 5 committed checksum vectors
- partial-sum composition across 2 committed even and odd split cases
- seeded partial accumulation against 3 widened-accumulator reference cases
- carry-discipline edge cases across 4 committed helper-local vectors
- 6 imported KUnit random-prefix lengths through the committed fixture corpus
- pseudo-header accumulation parity for the committed IPv4 UDP-style checksum vector
- IPv6 pseudo-header accumulation parity for 3 committed UDP, TCP, and ICMPv6-style checksum vectors, including the upper-length-bits regression fixture
- helper-local arithmetic regressions for `add`, `sub`, `negate`, shift rotation, and block composition invariants inside `lib/checksum.zig`
- 16-bit carry-helper parity for wrapped add and subtract edge cases before the incremental replacement helpers consume that contract
- incremental checksum replacement parity for payload word updates, 16-bit IPv4 header field replacement, 32-bit IPv4 address replacement, and diff-based checksum repair
- an external C-vs-Zig spot check through `python3 scripts/zigux/check-phase6-checksum-c-parity.py`, `zigux/tests/phase6_checksum_c_parity.zig`, and `zigux/tests/fixtures/phase6_checksum_c_harness.c` so the current `lib/checksum.c` arithmetic surface stays directly reviewable beside the committed Zig fixture packet; the live parity runner now replays 27 direct outputs across 5 compute cases, 3 seeded partial cases, 2 composition cases, 1 IPv4 pseudo-header nofold case, 3 IPv6 pseudo-header nofold cases, 4 carry-discipline folds, 5 direct `add16` and `sub16` carry-helper outputs, and 4 incremental replacement outputs
- shared fixture-backed checksum vectors stored in `zigux/tests/fixtures/phase6_checksum_vectors.zig` and consumed by `zigux/tests/phase6_checksum.zig`, while `lib/checksum.zig` keeps only helper-local arithmetic and regression checks so the leaf helper no longer depends on the shared Phase 6 fixture packet
- a replayable perf-sanity harness reports representative checksum cost per call and per byte while rechecking parity against the widened-accumulator `referencePartial` path on deterministic 64-byte and 1501-byte payloads, and it currently fail-closes on `max_slowdown_pct = 150` for both committed perf cases
- the shared `python3 scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py` guard now keeps that perf packet fail-closed around the per-call, per-byte, slowdown, folded-checksum, and reference-path markers before broader Phase 6 replay claims stay green

This is enough evidence to leave the bounded checksum helper lane parked unless a concrete new parity, perf, or directly coupled review-packet gap appears in the live repo.

## Non-goals

This slice does not yet claim:

- arch-specific assembly fast paths
- kbuild integration into the kernel proper
- performance equivalence across all architectures
- broader networking checksum families beyond the current bounded leaf-helper surface

## Next bounded step

Leave the checksum helper lane parked unless fresh repo inspection finds a concrete parity, perf, or directly coupled review-packet drift inside `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/fixtures/phase6_checksum_vectors.zig`, `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, `scripts/zigux/check-phase6-checksum-c-parity.py`, `zigux/tests/phase6_checksum_perf.zig`, or the shared Phase 6 packet. Current repo evidence shows the live checksum slice, parity script, parity runner, C harness, shared catalog, and machine-readable manifest agree on the 3-case IPv6 pseudo-header corpus, the 27-case checksum parity replay, and the 12-case checksum parity script self-test, while the broader shared `scripts/zigux/validate-phase6.py` packet still lags at `11` and is the next same-family follow-up. The next same-family follow-up should therefore stay narrow to that shared-validator drift rather than reopening `lib/checksum.zig` or its directly coupled checksum parity runners.
