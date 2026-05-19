# Phase 6 Checksum Slice

This document records a bounded Phase 6 leaf-helper validation slice for Zigux.

## Status

- `PHASE6_STATUS=parked`
- `PHASE6_SLICE=checksum-leaf-helper`
- scope: checksum helper parity and perf evidence already shipped on current `master`
- product boundary:
  - `lib/checksum.zig`
  - `zigux/tests/phase6_checksum.zig`
  - `zigux/tests/phase6_checksum_perf.zig`
  - `zigux/tests/fixtures/phase6_checksum_vectors.zig`

## Why this slice exists

Phase 6 is where Zigux can keep proving low-risk in-kernel helper ports without stepping into runtime-core or driver complexity.

`lib/checksum.c` stays a good bounded helper because it is:

- leaf-oriented
- semantics-heavy enough to need explicit parity coverage
- small enough to keep perf review bounded to compact fixed matrices

## Gates

1. run the focused helper replay
- `zigux/tests/phase6_checksum.zig` keeps the compute, partial, fold, replacement, folded and unfolded pseudo-header helpers, and aligned fast-path packet reviewable

2. run the bounded perf replay
- `zigux/tests/phase6_checksum_perf.zig` keeps the helper-vs-reference slowdown gate explicit through the committed `64B` and `1501B` payload matrix in `zigux/tests/fixtures/phase6_checksum_vectors.zig`
- the same perf replay also keeps `ipFastCsum()` honest through committed `IPV4_20B` and `IPV4_24B` aligned-header cases that compare the fast path directly against `compute()`

## Current parity and perf surface

The current checksum helper surface exercised by this slice covers:

- `add`, `sub`, `shift`, `blockAdd`, and `blockSub`
- `replace`, `replaceByDiff`, `replace2`, and `replace4`
- `from32to16`, `fold`, and `compute`
- `tcpUdpNofold`, `tcpUdpMagic`, `tcpUdpV6Nofold`, `tcpUdpV6Magic`, and `ipFastCsum`

The current tests and fixtures check:

- empty, odd-length, even-length, and seeded partial accumulation
- replacement and header-edit parity for payload words, IPv4 length edits, and IPv4 address edits
- folded and unfolded pseudo-header accumulation parity for IPv4 and IPv6
- aligned fast-path parity for minimal, updated, and option-bearing IPv4 headers
- perf-matrix stability for the committed `64B` and `1501B` fixture payloads with explicit slowdown thresholds
- aligned-header fast-path perf stability for the committed `IPV4_20B` and `IPV4_24B` fixture headers with explicit slowdown thresholds against `compute()`

## Non-goals

This slice does not yet claim:

- a restored direct C-vs-Zig parity checker on current `master`
- broader shared Phase 6 perf survey recovery
- any hexdump, base64, or bsearch packet changes

## Next bounded step

Leave this helper parked unless fresh repo inspection shows a concrete checksum-local parity, perf-matrix, or direct C parity drift. If this slice reopens soon, keep the next move inside `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, `zigux/tests/fixtures/phase6_checksum_vectors.zig`, or `scripts/zigux/check-phase6-checksum-c-parity.py` rather than widening into hexdump re-materialization or broader shared-note churn.
