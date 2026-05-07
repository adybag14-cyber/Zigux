# Phase 6 Perf Gate Survey

This document records the current shared measurement posture for the bounded Phase 6 leaf-helper packet on `master`.

## Status

- `PHASE6_PERF_SURVEY_STATUS=active`
- `PHASE6_PERF_PACKET=base64-bsearch-checksum-hexdump`
- roadmap anchor: Phase 6 requires `perf gates for math-sensitive helpers` while keeping the helper packet bounded to `lib/base64.zig`, `lib/bsearch.zig`, `lib/checksum.zig`, and `lib/hexdump.zig`
- shared replay note: the shared `make -C zigux phase6` route still stops at `phase6-validate` plus `phase6-test`; dedicated perf replays remain helper-local through `make -C zigux phase6-base64-perf`, `make -C zigux phase6-checksum-perf`, and `make -C zigux phase6-hexdump-perf`
- aggregated route note: `make -C zigux phase6-perf` now exists as a narrow convenience wrapper for `phase6-checksum-perf` plus `phase6-hexdump-perf`; it still excludes base64 even though `.github/workflows/zigux-bootstrap.yml` reruns `phase6-base64-perf` directly in CI
- owner-map note: `Documentation/zigux/phase6-leaf-helper-lane-sequencing.md` now separates packet-wide route truthfulness from helper-local threshold or replay-row edits inside this survey
- evidence note: the exact thresholds below were re-read from current `master` on `2026-05-07` by direct file inspection because this environment still cannot perform a safe local checkout or attached-toolchain replay

## Current Measurement Posture

- base64 shared posture: `zigux/tests/phase6_base64_perf.zig` still emits dedicated encode and decode slowdown markers for four fixture-backed replay cases, `zigux/tests/phase6_build.zig` still defines `phase6-base64-perf`, `zigux/Makefile` still exposes `make -C zigux phase6-base64-perf`, and `.github/workflows/zigux-bootstrap.yml` now reruns that base64 perf gate as its own direct CI step, while the shared `phase6` target and aggregate `phase6-perf` route still do not
- base64 exact thresholds: `zigux/tests/fixtures/phase6_base64_vectors.zig` still pins four perf cases (`STD_PAD`, `STD_NO_PAD`, `URLSAFE_PAD`, and `URLSAFE_NO_PAD`) at `iterations = 12000`, `max_encode_slowdown_pct = 150`, and `max_decode_slowdown_pct = 325`
- bsearch shared posture: the live executable measurement evidence remains the algorithmic comparison-budget replay inside `zigux/tests/phase6_bsearch.zig`, not a separate wall-clock perf harness
- bsearch exact evidence: the current 15-element typed and raw replay packet still requires `counted_compare_calls <= 4` across five representative typed lookups and `counted_raw_compare_calls <= 4` across five representative raw lookups, which keeps the packet aligned with the expected `std.math.log2_int_ceil(len) + 1` search budget without widening into standalone nanosecond thresholds
- bsearch review-surface posture: `Documentation/zigux/phase6-bsearch-slice.md`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_build.zig`, and `zigux/Makefile` now agree that the shipped bsearch packet uses inline sorted inputs plus the bundled comparison-budget replay rather than a separate fixture module or standalone `phase6_bsearch_perf` route
- checksum shared posture: a dedicated slowdown gate remains wired through `zigux/tests/phase6_checksum_perf.zig`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`
- checksum exact thresholds: `zigux/tests/fixtures/phase6_checksum_vectors.zig` still pins two perf cases, `64B` at `iterations = 200_000` and `1501B` at `iterations = 12_000`, with `max_slowdown_pct = 150` for both cases
- hexdump shared posture: a dedicated slowdown gate remains wired through `zigux/tests/phase6_hexdump_perf.zig`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`
- hexdump exact thresholds: `zigux/tests/fixtures/phase6_hexdump_vectors.zig` still pins `16B-plain-g1` at `reps = 40_000` with `max_slowdown_pct = 175`, `32B-ascii-g2` at `reps = 10_000` with `max_slowdown_pct = 550`, `16B-ascii-g4` at `reps = 20_000` with `max_slowdown_pct = 550`, and `16B-ascii-g8` at `reps = 20_000` with `max_slowdown_pct = 600`

## Roadmap Gap Summary

- the current packet keeps exact helper-local perf evidence for `base64`, `checksum`, and `hexdump`, with `bsearch` still reviewable through a bounded algorithmic comparison-budget replay rather than a timing gate
- the bundled `phase6` and aggregate `phase6-perf` make routes still replay only the shared helper tests plus the checksum and hexdump dedicated perf gates, while `.github/workflows/zigux-bootstrap.yml` separately reruns the base64 perf gate as its own direct CI step
- the convenience `make -C zigux phase6-perf` route now truthfully summarizes that shared perf posture on `master` by aggregating only the checksum and hexdump gates while leaving the base64 perf gate as a separate helper-local make route and direct workflow step
- helper-local threshold, replay-count, or fixture-label edits inside this survey still belong to the owning helper lane even though they appear in a shared note; reopen the shared sequencing lane only when the packet-wide route or owner split changes
- future same-lane follow-up should stay inside exact-threshold evidence, shared-route truthfulness, or the smallest shared replay repair that closes one of those specific gaps without widening into helper-semantic work

## Next Bounded Step

If this survey reopens, first diff `Documentation/zigux/phase6-perf-gate-survey.md`, `Documentation/zigux/phase6-leaf-helper-lane-sequencing.md`, `Documentation/zigux/phase6-bsearch-slice.md`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/fixtures/phase6_checksum_vectors.zig`, `zigux/tests/fixtures/phase6_hexdump_vectors.zig`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` together on current `master`, then decide whether the next honest move is a shared-route change or another narrowly scoped helper-local or review-surface repair.
