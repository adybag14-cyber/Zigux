# Phase 6 Helper Parity Catalog

This survey records the broader helper-parity companion for the bounded Phase 6 leaf-helper packet on `master`.

- surveyed head: `current-master-readback-2026-05-20`
- lane scope: public-tree-backed helper parity rows only
- direct helper-evidence companion: `Documentation/zigux/phase6-helper-evidence-catalog.md`
- shared machine-readable manifest: `zigux/tests/phase6_helper_parity_manifest.json`
- returned helper-evidence manifest: `zigux/tests/phase6_helper_evidence_manifest.json`
- roadmap-backed helper anchors:
  - `lib/base64.c`
  - `lib/bsearch.c`
  - `lib/checksum.c`
  - `lib/hexdump.c`

## Why this catalog exists

The helper-evidence catalog already keeps the directly readable shared Phase 6 packet honest. This parity companion keeps one compact helper-evidence row per roadmap anchor so broader reminder surfaces can point at a real survey instead of a missing file.

## Current helper-parity rows

### base64

- roadmap anchor: `lib/base64.c`
- landed Zig helper: `lib/base64.zig`
- focused helper replay: `zigux/tests/phase6_base64.zig`
- helper-evidence row: `zigux/tests/phase6_base64_perf.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, `scripts/zigux/check-phase6-base64-corpus-determinism.py`, `Documentation/zigux/phase6-base64-slice.md`, `Documentation/zigux/phase6-helper-evidence-catalog.md`, `zigux/tests/phase6_helper_evidence_manifest.json`, and `zigux/tests/phase6_helper_parity_manifest.json`
- exact missing direct companions from authenticated 2026-05-20 readback: `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig`, `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/phase6_base64_c_casegen.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`
- current posture: direct helper readback is restored for the helper, focused replay, perf replay, fixture surface, dedicated corpus checker, and slice note, while the exact missing direct companions above still returned 404 on 2026-05-20 and therefore remain outside shipped evidence

### bsearch

- roadmap anchor: `lib/bsearch.c`
- landed Zig helper: `lib/bsearch.zig`
- focused helper replay: `zigux/tests/phase6_bsearch.zig`
- helper-evidence row: `zigux/tests/phase6_bsearch_perf.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, `zigux/tests/phase6_bsearch_c_abi_budget.zig`, `zigux/tests/fixtures/phase6_bsearch_vectors.zig`, `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`, `Documentation/zigux/phase6-bsearch-slice.md`, `Documentation/zigux/phase6-helper-evidence-catalog.md`, `zigux/tests/phase6_helper_evidence_manifest.json`, and `zigux/tests/phase6_helper_parity_manifest.json`
- current posture: direct helper readback is restored across the helper, focused replay, perf replay, C ABI review routes, fixture surface, checker, and slice note

### checksum

- roadmap anchor: `lib/checksum.c`
- landed Zig helper: `lib/checksum.zig`
- focused helper replay: `zigux/tests/phase6_checksum.zig`
- helper-evidence row: `zigux/tests/phase6_checksum_perf.zig`, `zigux/tests/fixtures/phase6_checksum_vectors.zig`, `scripts/zigux/check-phase6-checksum-corpus-evidence.py`, `Documentation/zigux/phase6-checksum-slice.md`, `Documentation/zigux/phase6-helper-evidence-catalog.md`, `zigux/tests/phase6_helper_evidence_manifest.json`, and `zigux/tests/phase6_helper_parity_manifest.json`
- exact missing direct companions from authenticated 2026-05-20 readback: `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`
- current posture: direct helper readback is restored for the helper, focused replay, fixture-owned perf packet, checker, and slice note, while the exact missing direct companions above still returned 404 on 2026-05-20 and therefore remain outside shipped evidence

### hexdump

- roadmap anchor: `lib/hexdump.c`
- landed Zig helper: `lib/hexdump.zig`
- focused helper replay: `zigux/tests/phase6_hexdump.zig`
- helper-evidence row: `zigux/tests/phase6_hexdump_perf.zig`, `zigux/tests/phase6_hexdump_perf_matrix.zig`, `zigux/tests/fixtures/phase6_hexdump_vectors.zig`, `scripts/zigux/check-phase6-hexdump-packet.py`, `Documentation/zigux/phase6-hexdump-slice.md`, `Documentation/zigux/phase6-hexdump-perf-refresh.md`, `Documentation/zigux/phase6-helper-evidence-catalog.md`, `zigux/tests/phase6_helper_evidence_manifest.json`, and `zigux/tests/phase6_helper_parity_manifest.json`
- current posture: direct helper readback is restored across the helper, focused replay, perf replay, perf-matrix preflight, fixture surface, checker, slice note, and perf-refresh rationale note

## Shared parity boundary

Treat this file as the broader parity companion for the current helper-evidence packet rather than as a substitute for the directly readable shared packet in `Documentation/zigux/phase6-helper-evidence-catalog.md`, `zigux/tests/phase6_helper_evidence_manifest.json`, `zigux/tests/phase6_helper_parity_manifest.json`, `scripts/zigux/check-phase6-shared-surface.py`, `scripts/zigux/check-phase6-present-entrypoints.py`, `zigux/tests/phase6_build.zig`, and `zigux/Makefile`.

Reopen this catalog only when one of the four roadmap anchors gains or loses a truthful helper-evidence row on `master`.
