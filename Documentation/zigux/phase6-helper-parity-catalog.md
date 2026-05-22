# Phase 6 Helper Parity Catalog

This survey records the broader helper-parity companion for the bounded Phase 6 leaf-helper packet on `master`.

- surveyed head: `current-master-readback-2026-05-21`
- lane scope: directly readable helper parity rows and shared companion notes only
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
- current posture: direct helper readback is restored for the helper, focused replay, perf replay, fixture surface, dedicated corpus checker, direct C parity runner, direct C parity harness, direct C parity checker, and slice note. A follow-up authenticated current-master readback on 2026-05-22 directly recovered `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`, while `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig` and `zigux/tests/phase6_base64_c_casegen.zig` still remain outside shipped evidence

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
- helper-evidence row: `zigux/tests/phase6_checksum_perf.zig`, `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_vectors.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, `scripts/zigux/check-phase6-checksum-corpus-evidence.py`, `scripts/zigux/check-phase6-checksum-c-parity.py`, `Documentation/zigux/phase6-checksum-slice.md`, `Documentation/zigux/phase6-helper-evidence-catalog.md`, and `zigux/tests/phase6_helper_evidence_manifest.json`, and `zigux/tests/phase6_helper_parity_manifest.json`
- current posture: direct helper readback is restored for the helper, focused replay, fixture-owned perf packet, direct C parity runner, direct C parity harness, direct C parity checker, and slice note, so the checksum row now ships the same external parity review hook as the other portability-sensitive Phase 6 helpers without reopening hexdump work

### hexdump

- roadmap anchor: `lib/hexdump.c`
- landed Zig helper: `lib/hexdump.zig`
- focused helper replay: `zigux/tests/phase6_hexdump.zig`
- helper-evidence row: `zigux/tests/phase6_hexdump_perf.zig`, `zigux/tests/phase6_hexdump_perf_matrix.zig`, `zigux/tests/fixtures/phase6_hexdump_vectors.zig`, `scripts/zigux/check-phase6-hexdump-packet.py`, `scripts/zigux/check-phase6-hexdump-route.py`, `Documentation/zigux/phase6-hexdump-slice.md`, `Documentation/zigux/phase6-hexdump-perf-refresh.md`, `Documentation/zigux/phase6-helper-evidence-catalog.md`, `zigux/tests/phase6_helper_evidence_manifest.json`, and `zigux/tests/phase6_helper_parity_manifest.json`
- current posture: direct helper readback is restored across the helper, focused replay, perf replay, perf-matrix preflight, fixture surface, packet checker, route checker, slice note, and perf-refresh rationale note

## Shared parity boundary

Treat this file as the broader parity companion for the current helper-evidence packet rather than as a substitute for the directly readable shared packet in `Documentation/zigux/phase6-helper-evidence-catalog.md`, `zigux/tests/phase6_helper_evidence_manifest.json`, `zigux/tests/phase6_helper_parity_manifest.json`, `scripts/zigux/check-phase6-shared-surface.py`, `scripts/zigux/check-phase6-present-entrypoints.py`, `scripts/zigux/validate-phase6.py`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `Documentation/zigux/phase6-perf-gate-survey.md`.

Authenticated follow-up readback on 2026-05-21 directly recovered `Documentation/zigux/phase6-perf-gate-survey.md` again, so broader reminder surfaces can keep that survey inside the directly readable shared packet instead of treating it as fallback-only evidence.

Reopen this catalog only when one of the four roadmap anchors gains or loses a truthful helper-evidence row on `master`.
