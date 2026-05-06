# Phase 6 Perf Gate Survey

This document records the current shared measurement posture for the bounded Phase 6 leaf-helper packet on `master`.

## Status

- `PHASE6_PERF_SURVEY_STATUS=active`
- `PHASE6_PERF_PACKET=base64-bsearch-checksum-hexdump`
- roadmap anchor: Phase 6 requires `perf gates for math-sensitive helpers` while keeping the helper packet bounded to `lib/base64.zig`, `lib/bsearch.zig`, `lib/checksum.zig`, and `lib/hexdump.zig`
- shared replay note: there is still no aggregated `phase6-perf` route on current `master`; `make -C zigux phase6` remains the shared validation-plus-tests route, while dedicated perf replays stay helper-local

## Current Measurement Posture

- base64: a dedicated slowdown harness exists in `zigux/tests/phase6_base64_perf.zig`, and `zigux/tests/phase6_build.zig` still defines `phase6-base64-perf`, but `zigux/Makefile` and `.github/workflows/zigux-bootstrap.yml` do not currently replay that harness on the shared route
- base64 thresholds: the live harness still carries the current encode and decode slowdown ceilings through `zigux/tests/fixtures/phase6_base64_vectors.zig`, with the shared packet still relying on helper-local evidence rather than a shipped `make -C zigux phase6-base64-perf` route
- bsearch: the current measurement evidence is the comparison-budget replay inside `zigux/tests/phase6_bsearch.zig`, where representative typed and raw lookups over the current 15-element packet stay within four comparator calls instead of using a separate wall-clock perf gate
- checksum: a dedicated slowdown gate remains wired through `zigux/tests/phase6_checksum_perf.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`, with the current 150% ceiling still applied to the `64B` and `1501B` replay cases
- hexdump: a dedicated slowdown gate remains wired through `zigux/tests/phase6_hexdump_perf.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`, with the current grouped slowdown ceilings still set to `175` for `16B-plain-g1`, `550` for `32B-ascii-g2` and `16B-ascii-g4`, and `600` for `16B-ascii-g8`

## Roadmap Gap Summary

- the current packet fully ships dedicated slowdown gates for `checksum` and `hexdump`
- the current packet carries helper-local slowdown evidence for `base64`, but that harness is not part of the shared `make` or workflow replay path on `master`
- the current packet keeps `bsearch` reviewable through an algorithmic comparison-budget check rather than a dedicated timing gate
- future same-lane follow-up should stay inside survey truthfulness or the smallest shared perf-routing repair that closes one of those explicit gaps without widening into helper-semantic work

## Next Bounded Step

If this survey reopens, first diff `Documentation/zigux/phase6-perf-gate-survey.md`, `zigux/tests/phase6_base64_perf.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_checksum_perf.zig`, `zigux/tests/phase6_hexdump_perf.zig`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` together on current `master`, then decide whether the next honest move is another survey refresh or a narrowly scoped shared perf-route repair.
