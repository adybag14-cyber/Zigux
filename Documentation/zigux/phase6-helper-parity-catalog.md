# Phase 6 Helper Parity Catalog

This catalog records the current shared review surface for the bounded Phase 6 leaf-helper packet on `master`.

## Status

- `PHASE6_STATUS=parked`
- `PHASE6_PACKET=base64-bsearch-checksum-hexdump`
- surveyed head: `3ea8f93`
- roadmap anchors:
  - `lib/base64.c`
  - `lib/bsearch.c`
  - `lib/checksum.c`
  - `lib/hexdump.c`
- verification note: this catalog was refreshed by direct readback of the current `master` Phase 6 slice notes, shared docs indexes, perf survey, build entrypoint, Makefile routes, helper parity manifest, and the shared owner map on `2026-05-10`

## Why this catalog exists

The four Phase 6 slice notes remain the right place for helper-local detail, but the current packet still benefits from one shared note that lines up the roadmap anchors, the landed Zig helpers, and the reviewable evidence that already exists on `master`. This keeps the packet easier to audit without widening into new helper semantics, validator churn, or perf-policy changes.

## Shared Packet Surface

- docs root: `Documentation/zigux/README.md`
- reviewer checklist: `Documentation/zigux/review-checklist.md`
- owner map: `Documentation/zigux/phase6-leaf-helper-lane-sequencing.md`
- scripts index: `scripts/zigux/README.md`
- tests index: `zigux/tests/README.md`
- perf posture note: `Documentation/zigux/phase6-perf-gate-survey.md`
- shared build route: `zigux/tests/phase6_build.zig`
- Linux-style replay routes: `zigux/Makefile`
- shared packet manifest: `zigux/tests/phase6_helper_parity_manifest.json`

Use `Documentation/zigux/phase6-leaf-helper-lane-sequencing.md` before reopening any shared Phase 6 surface: packet-wide route and ownership repairs belong to the shared sequencing lane, but helper-row edits inside the shared catalog, perf survey, or manifest still route back to the owning helper lane.

## Current Helper Rows

### base64

- roadmap anchor: `lib/base64.c`
- Zig helper: `lib/base64.zig`
- focused replay: `zigux/tests/phase6_base64.zig`
- direct C parity replay: `zigux/tests/phase6_base64_c_parity.zig`
- dedicated perf replay: `zigux/tests/phase6_base64_perf.zig`
- committed fixture surfaces: `zigux/tests/fixtures/phase6_base64_vectors.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`
- dedicated external parity checker: `scripts/zigux/check-phase6-base64-c-parity.py`
- slice note: `Documentation/zigux/phase6-base64-slice.md`
- current review posture: functional parity plus the shipped direct 24-case C-vs-Zig spot check through the dedicated parity replay, C harness, and checker script, including returned `chars` and `bytes` sizing parity beside representative encode, decode, and malformed-tail rejection coverage, alongside the dedicated helper-local encode and decode slowdown gate exposed through `make -C zigux phase6-base64-perf`

### bsearch

- roadmap anchor: `lib/bsearch.c`
- Zig helper: `lib/bsearch.zig`
- focused replay: `zigux/tests/phase6_bsearch.zig`
- roadmap-facing parity surface: raw `bsearch` and `bsearchMutable` replay kept explicit inside `zigux/tests/phase6_bsearch.zig`
- focused lower- and upper-bound C ABI replay: `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`
- focused direct C ABI equality-budget replay: `zigux/tests/phase6_bsearch_c_abi_budget.zig`
- shared build route: `zigux/tests/phase6_build.zig`
- focused helper rerun route: `make -C zigux phase6-bsearch-test`
- direct local rerun route: `zig build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig`
- slice note: `Documentation/zigux/phase6-bsearch-slice.md`
- current review posture: functional parity plus bounded comparison-budget evidence inside the focused replay, alongside the dedicated bounds-focused C ABI companion and the dedicated direct C ABI equality-budget replay that keep the typed and raw lower-bound, upper-bound, and equality comparator contract reviewable without widening into a separate timing-style perf target in the shipped packet today

### checksum

- roadmap anchor: `lib/checksum.c`
- Zig helper: `lib/checksum.zig`
- focused replay: `zigux/tests/phase6_checksum.zig`
- direct C parity replay: `zigux/tests/phase6_checksum_c_parity.zig`
- dedicated perf replay: `zigux/tests/phase6_checksum_perf.zig`
- committed fixture surfaces: `zigux/tests/fixtures/phase6_checksum_vectors.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`
- dedicated external parity checker: `scripts/zigux/check-phase6-checksum-c-parity.py`
- slice note: `Documentation/zigux/phase6-checksum-slice.md`
- current review posture: helper parity plus the shipped direct 41-case C-vs-Zig replay through the dedicated parity replay, C harness, and checker script, alongside the dedicated slowdown gate exposed through `make -C zigux phase6-checksum-perf`

### hexdump

- roadmap anchor: `lib/hexdump.c`
- Zig helper: `lib/hexdump.zig`
- focused replay: `zigux/tests/phase6_hexdump.zig`
- dedicated perf replay: `zigux/tests/phase6_hexdump_perf.zig`
- committed fixture surface: `zigux/tests/fixtures/phase6_hexdump_vectors.zig`
- focused helper rerun route: `make -C zigux phase6-hexdump-test`
- direct local rerun route: `zig build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig`
- slice note: `Documentation/zigux/phase6-hexdump-slice.md`
- current review posture: helper parity is now individually rerunnable through `zig build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig` and `make -C zigux phase6-hexdump-test`, alongside the shipped formatter-sensitive slowdown gate exposed through `make -C zigux phase6-hexdump-perf`
- exact slowdown thresholds: `16B-plain-g1` at `reps = 40_000` with `max_slowdown_pct = 175`, `32B-ascii-g2` at `reps = 10_000` with `max_slowdown_pct = 550`, `16B-ascii-g4` at `reps = 20_000` with `max_slowdown_pct = 550`, and `16B-ascii-g8` at `reps = 20_000` with `max_slowdown_pct = 600`

## Shared Replay Reminders

- `zig build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig`
- `zig build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6-bsearch-test`
- `make -C zigux phase6-hexdump-test`
- `make -C zigux phase6-validate`
- `make -C zigux phase6`
- `make -C zigux phase6-base64-perf`
- `make -C zigux phase6-checksum-perf`
- `make -C zigux phase6-hexdump-perf`
- `make -C zigux phase6-perf`

## Next Bounded Step

Reopen this catalog only when one of the four roadmap anchors gains, loses, or materially changes a reviewable helper-evidence row on `master`, or when the shared `phase6` or `phase6-perf` routes change enough that this summary would stop being exact. When the drift is packet-wide, repair it through `Documentation/zigux/phase6-leaf-helper-lane-sequencing.md`; when the drift changes only one helper row, route the follow-up back to that helper-owned lane instead.
