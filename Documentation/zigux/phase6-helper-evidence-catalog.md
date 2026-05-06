# Phase 6 Helper Evidence Catalog

This note records the current helper-evidence survey for the Phase 6 leaf-helper packet at the inspected `master` tip.

- inspected head: `d198f036eb3ef64b2c5fb5ff3f52ed596e8adfa9`
- lane scope: shared helper-evidence rows only
- roadmap-backed helper anchors:
  - `lib/base64.c`
  - `lib/bsearch.c`
  - `lib/checksum.c`
  - `lib/hexdump.c`

## Why this catalog exists

The four Phase 6 slice notes stay useful for helper-local detail, but they do not gather the roadmap anchor, the landed Zig helper, and the current reviewable evidence row in one place. This catalog closes that narrower review gap without widening the Phase 6 packet into new perf policy or validator work.

## Current helper-evidence rows

### base64

- roadmap anchor: `lib/base64.c`
- Zig helper: `lib/base64.zig`
- focused replay: `zigux/tests/phase6_base64.zig`
- committed fixture surface: `zigux/tests/fixtures/phase6_base64_vectors.zig`
- shared build route: `zigux/tests/phase6_build.zig`
- slice note: `Documentation/zigux/phase6-base64-slice.md`
- current review posture: functional parity only on `master`; there is no dedicated base64 perf gate in the shipped Phase 6 packet today

### bsearch

- roadmap anchor: `lib/bsearch.c`
- Zig helper: `lib/bsearch.zig`
- focused replay: `zigux/tests/phase6_bsearch.zig`
- shared build route: `zigux/tests/phase6_build.zig`
- slice note: `Documentation/zigux/phase6-bsearch-slice.md`
- current review posture: functional parity plus bounded comparison-budget assertions inside `zigux/tests/phase6_bsearch.zig`; there is no separate dedicated bsearch perf target on `master`

### checksum

- roadmap anchor: `lib/checksum.c`
- Zig helper: `lib/checksum.zig`
- focused replay: `zigux/tests/phase6_checksum.zig`
- dedicated perf gate: `zigux/tests/phase6_checksum_perf.zig`
- committed fixture surface: `zigux/tests/fixtures/phase6_checksum_vectors.zig`
- shared build route: `zigux/tests/phase6_build.zig`
- slice note: `Documentation/zigux/phase6-checksum-slice.md`
- current review posture: helper parity plus the shipped `make -C zigux phase6-checksum-perf` slowdown gate

### hexdump

- roadmap anchor: `lib/hexdump.c`
- Zig helper: `lib/hexdump.zig`
- focused replay: `zigux/tests/phase6_hexdump.zig`
- dedicated perf gate: `zigux/tests/phase6_hexdump_perf.zig`
- committed fixture surface: `zigux/tests/fixtures/phase6_hexdump_vectors.zig`
- shared build route: `zigux/tests/phase6_build.zig`
- slice note: `Documentation/zigux/phase6-hexdump-slice.md`
- current review posture: helper parity plus the shipped `make -C zigux phase6-hexdump-perf` formatter-sensitive perf gate

## Shared replay reminders

- `make -C zigux phase6-validate`
- `make -C zigux phase6`
- `make -C zigux phase6-checksum-perf`
- `make -C zigux phase6-hexdump-perf`

Reopen this catalog only when one of the four roadmap anchors gains or loses a reviewable helper-evidence row on `master`.
