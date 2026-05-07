# Phase 6 Helper Parity Catalog

This catalog records the current shared review surface for the bounded Phase 6 leaf-helper packet on `master`.

## Status

- `PHASE6_STATUS=parked`
- `PHASE6_PACKET=base64-bsearch-checksum-hexdump`
- roadmap anchors:
  - `lib/base64.c`
  - `lib/bsearch.c`
  - `lib/checksum.c`
  - `lib/hexdump.c`
- verification note: this catalog was refreshed by direct readback of the current `master` Phase 6 slice notes, shared docs indexes, perf survey, build entrypoint, Makefile routes, and helper parity manifest on `2026-05-07`, with inspected head `affdebd460c9c33ce939c7535cdb929352648e93`

## Why this catalog exists

The four Phase 6 slice notes remain the right place for helper-local detail, but the current packet still benefits from one shared note that lines up the roadmap anchors, the landed Zig helpers, and the reviewable evidence that already exists on `master`. This keeps the packet easier to audit without widening into new helper semantics, validator churn, or perf-policy changes.

## Shared Packet Surface

- docs root: `Documentation/zigux/README.md`
- reviewer checklist: `Documentation/zigux/review-checklist.md`
- scripts index: `scripts/zigux/README.md`
- tests index: `zigux/tests/README.md`
- perf posture note: `Documentation/zigux/phase6-perf-gate-survey.md`
- shared build route: `zigux/tests/phase6_build.zig`
- Linux-style replay routes: `zigux/Makefile`
- shared packet manifest: `zigux/tests/phase6_helper_parity_manifest.json`

## Current Helper Rows

### base64

- roadmap anchor: `lib/base64.c`
- Zig helper: `lib/base64.zig`
- focused replay: `zigux/tests/phase6_base64.zig`
- dedicated perf replay: `zigux/tests/phase6_base64_perf.zig`
- committed fixture surface: `zigux/tests/fixtures/phase6_base64_vectors.zig`
- slice note: `Documentation/zigux/phase6-base64-slice.md`
- current review posture: functional parity plus a dedicated helper-local encode and decode slowdown gate; the replay remains individually runnable through `make -C zigux phase6-base64-perf` rather than bundled into the shared `phase6` route

### bsearch

- roadmap anchor: `lib/bsearch.c`
- Zig helper: `lib/bsearch.zig`
- focused replay: `zigux/tests/phase6_bsearch.zig`
- shared build route: `zigux/tests/phase6_build.zig`
- slice note: `Documentation/zigux/phase6-bsearch-slice.md`
- current review posture: functional parity plus bounded comparison-budget evidence inside the focused replay; there is no separate timing-style perf target in the shipped packet today

### checksum

- roadmap anchor: `lib/checksum.c`
- Zig helper: `lib/checksum.zig`
- focused replay: `zigux/tests/phase6_checksum.zig`
- dedicated perf replay: `zigux/tests/phase6_checksum_perf.zig`
- committed fixture surface: `zigux/tests/fixtures/phase6_checksum_vectors.zig`
- slice note: `Documentation/zigux/phase6-checksum-slice.md`
- current review posture: helper parity plus the shipped dedicated slowdown gate exposed through `make -C zigux phase6-checksum-perf`

### hexdump

- roadmap anchor: `lib/hexdump.c`
- Zig helper: `lib/hexdump.zig`
- focused replay: `zigux/tests/phase6_hexdump.zig`
- dedicated perf replay: `zigux/tests/phase6_hexdump_perf.zig`
- committed fixture surface: `zigux/tests/fixtures/phase6_hexdump_vectors.zig`
- slice note: `Documentation/zigux/phase6-hexdump-slice.md`
- current review posture: helper parity plus the shipped formatter-sensitive slowdown gate exposed through `make -C zigux phase6-hexdump-perf`

## Shared Replay Reminders

- `make -C zigux phase6-validate`
- `make -C zigux phase6`
- `make -C zigux phase6-base64-perf`
- `make -C zigux phase6-checksum-perf`
- `make -C zigux phase6-hexdump-perf`
- `make -C zigux phase6-perf`

## Next Bounded Step

Reopen this catalog only when one of the four roadmap anchors gains, loses, or materially changes a reviewable helper-evidence row on `master`, or when the shared `phase6` or `phase6-perf` routes change enough that this summary would stop being exact.
