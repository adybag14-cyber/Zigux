# Phase 6 Perf Gate Survey

This document records the current shared measurement posture for the bounded Phase 6 leaf-helper packet on `master`.

## Status

- `PHASE6_PERF_SURVEY_STATUS=active`
- `PHASE6_PERF_PACKET=base64-bsearch-checksum-hexdump`
- roadmap anchor: Phase 6 requires `perf gates for math-sensitive helpers` while keeping the helper packet bounded to `lib/base64.zig`, `lib/bsearch.zig`, `lib/checksum.zig`, and `lib/hexdump.zig`
- shared replay note: the shared `make -C zigux phase6` route still stops at `phase6-validate` plus `phase6-test`; dedicated perf replays remain helper-local through `make -C zigux phase6-base64-perf`, `make -C zigux phase6-checksum-perf`, and `make -C zigux phase6-hexdump-perf`
- evidence note: the exact thresholds below were re-read from current `master` on `2026-05-06` by direct file inspection because this environment still cannot perform a safe local checkout or attached-toolchain replay

## Current Measurement Posture

- base64 shared posture: `zigux/tests/phase6_base64_perf.zig` still emits dedicated encode and decode slowdown markers for four fixture-backed replay cases, `zigux/tests/phase6_build.zig` still defines `phase6-base64-perf`, and `zigux/Makefile` still exposes `make -C zigux phase6-base64-perf`, but neither the shared `phase6` target nor `.github/workflows/zigux-bootstrap.yml` replays that base64 perf gate on the bundled route
- base64 exact thresholds: `zigux/tests/fixtures/phase6_base64_vectors.zig` still pins four perf cases (`STD_PAD`, `STD_NO_PAD`, `URLSAFE_PAD`, and `URLSAFE_NO_PAD`) at `iterations = 12000`, `max_encode_slowdown_pct = 150`, and `max_decode_slowdown_pct = 150`
- bsearch shared posture: the live executable measurement evidence remains the algorithmic comparison-budget replay inside `zigux/tests/phase6_bsearch.zig`, not a separate wall-clock perf harness
- bsearch exact evidence: the current 15-element typed and raw replay packet still requires `counted_compare_calls <= 4` across five representative typed lookups and `counted_raw_compare_calls <= 4` across five representative raw lookups, which keeps the packet aligned with the expected `std.math.log2_int_ceil(len) + 1` search budget without widening into standalone nanosecond thresholds
- bsearch survey drift: `Documentation/zigux/phase6-bsearch-slice.md` still names `zigux/tests/phase6_bsearch_perf.zig`, `zigux/tests/fixtures/phase6_bsearch_vectors.zig`, and `make -C zigux phase6-perf`, but those files and routes are not present in `zigux/tests/phase6_build.zig`, `zigux/Makefile`, or `.github/workflows/zigux-bootstrap.yml` on current `master`
- checksum shared posture: a dedicated slowdown gate remains wired through `zigux/tests/phase6_checksum_perf.zig`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`
- checksum exact thresholds: `zigux/tests/fixtures/phase6_checksum_vectors.zig` still pins two perf cases, `64B` at `iterations = 200_000` and `1501B` at `iterations = 12_000`, with `max_slowdown_pct = 150` for both cases
- hexdump shared posture: a dedicated slowdown gate remains wired through `zigux/tests/phase6_hexdump_perf.zig`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`
- hexdump exact thresholds: `zigux/tests/fixtures/phase6_hexdump_vectors.zig` still pins `16B-plain-g1` at `reps = 40_000` with `max_slowdown_pct = 175`, `32B-ascii-g2` at `reps = 10_000` with `max_slowdown_pct = 550`, `16B-ascii-g4` at `reps = 20_000` with `max_slowdown_pct = 550`, and `16B-ascii-g8` at `reps = 20_000` with `max_slowdown_pct = 600`

## Roadmap Gap Summary

- the current packet keeps exact helper-local perf evidence for `base64`, `checksum`, and `hexdump`, with `bsearch` still reviewable through a bounded algorithmic comparison-budget replay rather than a timing gate
- the current shared route fully replays only the `checksum` and `hexdump` dedicated perf gates in CI; `base64` remains individually runnable but not part of the bundled `phase6` or bootstrap workflow path
- the current packet still has a bsearch documentation truthfulness gap because the helper-local slice note overstates shipped files and routes that are absent on current `master`
- future same-lane follow-up should stay inside exact-threshold evidence, shared-route truthfulness, or the smallest shared replay repair that closes one of those specific gaps without widening into helper-semantic work

## Next Bounded Step

If this survey reopens, first diff `Documentation/zigux/phase6-perf-gate-survey.md`, `Documentation/zigux/phase6-bsearch-slice.md`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/fixtures/phase6_checksum_vectors.zig`, `zigux/tests/fixtures/phase6_hexdump_vectors.zig`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` together on current `master`, then decide whether the next honest move is a documentation truthfulness repair or a narrowly scoped shared perf-route change.