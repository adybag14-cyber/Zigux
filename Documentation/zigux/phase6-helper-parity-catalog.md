# Phase 6 Helper Parity Catalog

This survey records the broader helper-parity companion for the bounded Phase 6 leaf-helper packet on `master`.

- surveyed head: `current-master-readback-2026-05-22`
- lane scope: shared helper-parity rows and machine-readable manifest only
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

## Roadmap-to-helper-evidence row index

| helper | roadmap anchor | landed Zig helper | helper-evidence row highlights |
| --- | --- | --- | --- |
| `base64` | `lib/base64.c` | `lib/base64.zig` | `zigux/tests/phase6_base64_perf.zig`, `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, `zigux/tests/phase6_base64_c_parity_vectors.zig`, `zigux/tests/phase6_base64_c_casegen.zig`, `scripts/zigux/check-phase6-base64-corpus-determinism.py`, `scripts/zigux/check-phase6-base64-c-parity.py`, `Documentation/zigux/phase6-base64-slice.md`, `Documentation/zigux/phase6-helper-evidence-catalog.md`, `zigux/tests/phase6_helper_evidence_manifest.json`, `zigux/tests/phase6_helper_parity_manifest.json` |
| `bsearch` | `lib/bsearch.c` | `lib/bsearch.zig` | `zigux/tests/phase6_bsearch_perf.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, `zigux/tests/phase6_bsearch_c_abi_budget.zig`, `zigux/tests/phase6_bsearch_c_parity.zig`, `zigux/tests/fixtures/phase6_bsearch_c_harness.c`, `zigux/tests/fixtures/phase6_bsearch_vectors.zig`, `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`, `scripts/zigux/check-phase6-bsearch-c-parity.py`, `Documentation/zigux/phase6-bsearch-slice.md`, `Documentation/zigux/phase6-helper-evidence-catalog.md`, `zigux/tests/phase6_helper_evidence_manifest.json`, `zigux/tests/phase6_helper_parity_manifest.json` |
| `checksum` | `lib/checksum.c` | `lib/checksum.zig` | `zigux/tests/phase6_checksum_perf.zig`, `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_vectors.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, `scripts/zigux/check-phase6-checksum-corpus-evidence.py`, `scripts/zigux/check-phase6-checksum-c-parity.py`, `Documentation/zigux/phase6-checksum-slice.md`, `Documentation/zigux/phase6-helper-evidence-catalog.md`, `zigux/tests/phase6_helper_evidence_manifest.json`, `zigux/tests/phase6_helper_parity_manifest.json` |
| `hexdump` | `lib/hexdump.c` | `lib/hexdump.zig` | `zigux/tests/phase6_hexdump_perf.zig`, `zigux/tests/phase6_hexdump_perf_matrix.zig`, `zigux/tests/fixtures/phase6_hexdump_vectors.zig`, `scripts/zigux/check-phase6-hexdump-packet.py`, `scripts/zigux/check-phase6-hexdump-route.py`, `Documentation/zigux/phase6-hexdump-slice.md`, `Documentation/zigux/phase6-hexdump-perf-refresh.md`, `Documentation/zigux/phase6-helper-evidence-catalog.md`, `zigux/tests/phase6_helper_evidence_manifest.json`, `zigux/tests/phase6_helper_parity_manifest.json` |

Use this compact index as the row-level roadmap check first. The detailed helper sections below still carry the exact direct-readback posture and replay-specific context for each helper.

## Current helper-parity rows

### base64

- roadmap anchor: `lib/base64.c`
- landed Zig helper: `lib/base64.zig`
- focused helper replay: `zigux/tests/phase6_base64.zig`
- helper-evidence row: `zigux/tests/phase6_base64_perf.zig`, `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, `zigux/tests/phase6_base64_c_parity_vectors.zig`, `zigux/tests/phase6_base64_c_casegen.zig`, `scripts/zigux/check-phase6-base64-corpus-determinism.py`, `scripts/zigux/check-phase6-base64-c-parity.py`, `Documentation/zigux/phase6-base64-slice.md`, `Documentation/zigux/phase6-helper-evidence-catalog.md`, `zigux/tests/phase6_helper_evidence_manifest.json`, and `zigux/tests/phase6_helper_parity_manifest.json`
- current posture: direct helper readback is restored for the helper, focused replay, perf replay, fixture surface, dedicated corpus checker, direct C parity runner, direct C parity harness, direct C parity vectors companion, direct C parity casegen companion, direct C parity checker, and slice note. A targeted authenticated current-master reread on 2026-05-27 directly recovered `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig` and `zigux/tests/phase6_base64_c_casegen.zig`, so the base64 row no longer carries a known generator-side direct-readback gap.

### bsearch

- roadmap anchor: `lib/bsearch.c`
- landed Zig helper: `lib/bsearch.zig`
- focused helper replay: `zigux/tests/phase6_bsearch.zig`
- helper-evidence row: `zigux/tests/phase6_bsearch_perf.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, `zigux/tests/phase6_bsearch_c_abi_budget.zig`, `zigux/tests/phase6_bsearch_c_parity.zig`, `zigux/tests/fixtures/phase6_bsearch_c_harness.c`, `zigux/tests/fixtures/phase6_bsearch_vectors.zig`, `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`, `scripts/zigux/check-phase6-bsearch-c-parity.py`, `Documentation/zigux/phase6-bsearch-slice.md`, `Documentation/zigux/phase6-helper-evidence-catalog.md`, `zigux/tests/phase6_helper_evidence_manifest.json`, and `zigux/tests/phase6_helper_parity_manifest.json`
- current posture: direct helper readback is restored across the helper, focused replay, perf replay, C ABI review routes, direct C parity runner, direct C parity harness, fixture surface, dedicated corpus checker, direct C parity checker, and slice note
- direct C parity spot-check marker: `PHASE6_BSEARCH_C_PARITY_CASES=17`

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

Treat this file as the broader parity companion for the current helper-evidence packet rather than as a substitute for the directly readable shared packet in `Documentation/zigux/phase6-helper-evidence-catalog.md`, `zigux/tests/phase6_helper_evidence_manifest.json`, `zigux/tests/phase6_helper_parity_manifest.json`, `scripts/zigux/check-phase6-shared-surface.py`, `scripts/zigux/check-phase6-present-entrypoints.py`, `scripts/zigux/check-phase6-base64-bsearch-perf-markers.py`, `scripts/zigux/validate-phase6.py`, `scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py`, `scripts/zigux/check-phase6-perf-threshold-markers.py`, `scripts/zigux/check-phase6-hexdump-packet.py`, `scripts/zigux/check-phase6-hexdump-route.py`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `Documentation/zigux/phase6-perf-gate-survey.md`.

Authenticated follow-up readback on 2026-05-22 directly recovered `Documentation/zigux/phase6-perf-gate-survey.md` and `scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py` again, so broader reminder surfaces can keep the shared survey plus the base64-bsearch, checksum-hexdump, and perf-threshold guard surfaces inside the directly readable shared packet instead of treating any of those guards as fallback-only evidence.

A later direct perf-packet reread on 2026-05-25 also reconfirmed `Documentation/zigux/phase6-perf-gate-survey.md`, `scripts/zigux/validate-phase6.py`, `scripts/zigux/check-phase6-shared-surface.py`, the three dedicated Phase 6 perf-marker guards, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` still line up on current `master`, so this parity companion should keep treating the shared perf survey as a live directly readable surface rather than only a one-time 2026-05-22 recovery note.

Reopen this catalog only when one of the four roadmap anchors gains or loses a truthful helper-evidence row on `master`.
