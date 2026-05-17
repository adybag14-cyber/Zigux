# Phase 6 Helper Evidence Catalog

This note records the current helper-evidence survey for the bounded Phase 6 leaf-helper packet on `master`.

- surveyed head: `840f388`
- lane scope: shared helper-evidence rows only
- shared scripts-root reminder: `scripts/zigux/README.md`
- shared tests-root reminder: `zigux/tests/README.md`
- roadmap-backed helper anchors:
  - `lib/base64.c`
  - `lib/bsearch.c`
  - `lib/checksum.c`
  - `lib/hexdump.c`

## Why this catalog exists

The four Phase 6 slice notes keep the helper-local detail, but they do not keep one small shared table of the roadmap anchor, the landed Zig helper, and the current reviewable evidence row. This catalog closes that narrower review gap without widening the Phase 6 packet into new perf policy, validator, or helper-semantic work.

## Current direct-readback warning

Fresh direct GitHub contents reads on current `master` now return missing for several shared-note and helper-local packet members that older Phase 6 reminder surfaces still name as shipped evidence, including:

- `Documentation/zigux/phase6-helper-parity-catalog.md`
- `Documentation/zigux/phase6-perf-gate-survey.md`
- `zigux/tests/phase6_build.zig`
- `zigux/tests/phase6_helper_parity_manifest.json`
- `zigux/tests/phase6_base64.zig`
- `zigux/tests/phase6_bsearch.zig`
- `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`
- `zigux/tests/phase6_bsearch_c_abi_budget.zig`
- `zigux/tests/phase6_checksum.zig`
- `zigux/tests/phase6_hexdump.zig`
- `scripts/zigux/check-phase6-shared-surface.py`
- `scripts/zigux/check-phase6-present-entrypoints.py`
- `scripts/zigux/check-phase6-base64-c-parity.py`
- `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`
- `scripts/zigux/check-phase6-checksum-c-parity.py`
- `scripts/zigux/check-phase6-hexdump-packet.py`

Treat those paths as last-known Phase 6 packet members that require fresh reread or re-materialization before they are presented as current shipped direct evidence again. Keep this catalog aligned with that direct-readback limit instead of overstating shared-note or helper-local reviewability from older route names alone.

## Current helper-evidence rows

### base64

- roadmap anchor: `lib/base64.c`
- Zig helper: `lib/base64.zig`
- focused helper replay: `zigux/tests/phase6_base64.zig`
- dedicated slowdown replay: `zigux/tests/phase6_base64_perf.zig`
- committed fixture surfaces: `zigux/tests/fixtures/phase6_base64_vectors.zig` and `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig`
- direct C parity packet: `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`
- slice note: `Documentation/zigux/phase6-base64-slice.md`
- current review posture: the roadmap-backed base64 packet remains the intended bounded helper surface, but current direct evidence is limited to this shared catalog and the directly readable scripts-root plus tests-root reminders until fresh direct reads confirm the helper-local replay and parity members again

### bsearch

- roadmap anchor: `lib/bsearch.c`
- Zig helper: `lib/bsearch.zig`
- focused helper replay: `zigux/tests/phase6_bsearch.zig`
- focused lower- and upper-bound C ABI replay: `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`
- focused direct C ABI equality-budget replay: `zigux/tests/phase6_bsearch_c_abi_budget.zig`
- compact shared seed fixture companion: `zigux/tests/fixtures/phase6_bsearch_vectors.zig`
- direct corpus evidence checker: `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`
- slice note: `Documentation/zigux/phase6-bsearch-slice.md`
- current review posture: the roadmap-backed bsearch packet still names the right parity and comparison-budget surfaces, but current direct evidence is limited to this shared catalog and the directly readable scripts-root plus tests-root reminders until fresh direct reads confirm the helper-local replays and corpus checker again

### checksum

- roadmap anchor: `lib/checksum.c`
- Zig helper: `lib/checksum.zig`
- focused helper replay: `zigux/tests/phase6_checksum.zig`
- dedicated slowdown replay: `zigux/tests/phase6_checksum_perf.zig`
- committed fixture surface: `zigux/tests/fixtures/phase6_checksum_vectors.zig`
- direct C parity packet: `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`
- slice note: `Documentation/zigux/phase6-checksum-slice.md`
- current review posture: the roadmap-backed checksum packet remains intentionally bounded, but current direct evidence is limited to this shared catalog and the directly readable scripts-root plus tests-root reminders until fresh direct reads confirm the helper-local replay and parity members again

### hexdump

- roadmap anchor: `lib/hexdump.c`
- Zig helper: `lib/hexdump.zig`
- focused helper replay: `zigux/tests/phase6_hexdump.zig`
- dedicated slowdown replay: `zigux/tests/phase6_hexdump_perf.zig`
- exact perf-matrix preflight: `zigux/tests/phase6_hexdump_perf_matrix.zig`
- committed fixture surface: `zigux/tests/fixtures/phase6_hexdump_vectors.zig`
- helper-local packet checker: `scripts/zigux/check-phase6-hexdump-packet.py`
- perf refresh note: `Documentation/zigux/phase6-hexdump-perf-refresh.md`
- slice note: `Documentation/zigux/phase6-hexdump-slice.md`
- current review posture: the roadmap-backed hexdump packet still points at the right formatting and slowdown surfaces, but current direct evidence is limited to this shared catalog and the directly readable scripts-root plus tests-root reminders until fresh direct reads confirm the helper-local replay, checker, and perf companions again

## Last-known shared replay inventory

- `python3 scripts/zigux/check-phase6-base64-c-parity.py`
- `zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6-base64-perf`
- `python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py`
- `python3 scripts/zigux/check-phase6-checksum-c-parity.py`
- `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6-checksum-perf`
- `python3 scripts/zigux/check-phase6-hexdump-packet.py`
- `make -C zigux phase6-bsearch-test`
- `make -C zigux phase6-hexdump-review`
- `make -C zigux phase6-hexdump-test`
- `make -C zigux phase6-hexdump-perf`

Reopen this catalog only when one of the four roadmap anchors gains or loses a truthful helper-evidence row on `master`.
