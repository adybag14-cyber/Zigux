# Phase 6 Helper Evidence Catalog

This note records the current helper-evidence survey for the bounded Phase 6 leaf-helper packet on `master`.

- surveyed head: `61e026c`
- lane scope: shared helper-evidence rows and machine-readable manifest only
- shared scripts-root reminder: `scripts/zigux/README.md`
- shared tests-root reminder: `zigux/tests/README.md`
- shared docs-root reminder: `Documentation/zigux/README.md`
- directly readable shared build foothold: `zigux/tests/phase6_build.zig`
- shared machine-readable manifest: `zigux/tests/phase6_helper_evidence_manifest.json`
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
- `Documentation/zigux/phase6-hexdump-slice.md`
- `Documentation/zigux/phase6-hexdump-perf-refresh.md`
- `zigux/tests/phase6_helper_parity_manifest.json`
- `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig`
- `zigux/tests/phase6_base64_c_parity.zig`
- `zigux/tests/phase6_base64_c_casegen.zig`
- `zigux/tests/fixtures/phase6_base64_c_harness.c`
- `zigux/tests/phase6_hexdump_perf_matrix.zig`
- `scripts/zigux/check-phase6-base64-c-parity.py`
- `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`
- `scripts/zigux/check-phase6-checksum-c-parity.py`
- `scripts/zigux/check-phase6-hexdump-packet.py`

Treat those paths as last-known Phase 6 packet members that require fresh reread or re-materialization before they are presented as current shipped direct evidence again. Keep this catalog aligned with that direct-readback limit instead of overstating shared-note or helper-local reviewability from older route names alone. The directly readable shared packet in this environment is therefore this helper-evidence catalog together with `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase6-shared-surface.py`, `scripts/zigux/check-phase6-present-entrypoints.py`, and the restored shared build foothold `zigux/tests/phase6_build.zig`.

## Current helper-evidence rows

### base64

- roadmap anchor: `lib/base64.c`
- Zig helper: `lib/base64.zig`
- focused helper replay: `zigux/tests/phase6_base64.zig`
- dedicated slowdown replay: `zigux/tests/phase6_base64_perf.zig`
- committed fixture surface: `zigux/tests/fixtures/phase6_base64_vectors.zig`
- last-known direct C parity companions still needing fresh direct reads: `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig`, `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/phase6_base64_c_casegen.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`
- slice note: `Documentation/zigux/phase6-base64-slice.md`
- current review posture: the roadmap-backed base64 packet now has directly readable helper-local evidence through `lib/base64.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_base64_perf.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, `Documentation/zigux/phase6-base64-slice.md`, this shared catalog, the machine-readable manifest, the restored shared build foothold, and the directly readable scripts-root plus tests-root reminders, while the direct C parity companions still need fresh direct reads before they are presented as current shipped evidence

### bsearch

- roadmap anchor: `lib/bsearch.c`
- Zig helper: `lib/bsearch.zig`
- focused helper replay: `zigux/tests/phase6_bsearch.zig`
- focused C ABI replays: `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig` and `zigux/tests/phase6_bsearch_c_abi_budget.zig`
- compact shared seed fixture companion: `zigux/tests/fixtures/phase6_bsearch_vectors.zig`
- slice note: `Documentation/zigux/phase6-bsearch-slice.md`
- last-known companion packet members still needing fresh direct reads: `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`
- current review posture: direct helper-local evidence is readable again through `lib/bsearch.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, `zigux/tests/phase6_bsearch_c_abi_budget.zig`, `zigux/tests/fixtures/phase6_bsearch_vectors.zig`, `Documentation/zigux/phase6-bsearch-slice.md`, this shared catalog, the machine-readable manifest, the restored shared build foothold, and the directly readable scripts-root plus tests-root reminders, while the dedicated corpus checker still needs fresh direct reads before it is presented as current shipped evidence

### checksum

- roadmap anchor: `lib/checksum.c`
- Zig helper: `lib/checksum.zig`
- focused helper replay: `zigux/tests/phase6_checksum.zig`
- dedicated slowdown replay: `zigux/tests/phase6_checksum_perf.zig`
- committed fixture surface: `zigux/tests/fixtures/phase6_checksum_vectors.zig`
- direct C parity packet: `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`
- slice note: `Documentation/zigux/phase6-checksum-slice.md`
- current review posture: direct helper-local evidence is readable again through `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, `zigux/tests/fixtures/phase6_checksum_vectors.zig`, `Documentation/zigux/phase6-checksum-slice.md`, this shared catalog, the machine-readable manifest, the restored shared build foothold, and the directly readable scripts-root plus tests-root reminders, while the direct C parity companions still need fresh direct reads before they are presented as current shipped evidence

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
- current review posture: direct helper-local evidence is readable again through `lib/hexdump.zig`, `zigux/tests/phase6_hexdump.zig`, `zigux/tests/phase6_hexdump_perf.zig`, `zigux/tests/fixtures/phase6_hexdump_vectors.zig`, this shared catalog, the machine-readable manifest, the restored shared build foothold, and the directly readable scripts-root plus tests-root reminders, while the perf-matrix preflight, helper-local checker, perf refresh note, and slice note still need fresh direct reads before they are presented as current shipped evidence

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
