# Phase 6 Leaf-Helper Lane Sequencing

This note keeps the bounded Phase 6 leaf-helper packet from overlapping itself on `master`.

## Status

- `PHASE6_LANE_MAP_STATUS=active`
- `PHASE6_PACKET=base64-bsearch-checksum-hexdump`
- shared packet status source: `zigux/tests/phase6_helper_parity_manifest.json`
- shared packet catalog: `Documentation/zigux/phase6-helper-parity-catalog.md`
- shared perf posture note: `Documentation/zigux/phase6-perf-gate-survey.md`

## Shared-Surface Owner

Use this sequencing lane only for packet-wide routing, ownership, or anti-overlap truthfulness across:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase6-helper-parity-catalog.md`
- `Documentation/zigux/phase6-perf-gate-survey.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `scripts/zigux/check-phase6-shared-surface.py`
- `zigux/tests/phase6_build.zig`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`
- packet-level fields in `zigux/tests/phase6_helper_parity_manifest.json` such as `status`, `tranche`, `roadmap_anchors`, `shared_gates`, `exact_checks`, and shared route summaries

## Helper-Owned Lanes

### base64 packet

Keep helper-local work under:

- `lib/base64.zig`
- `zigux/tests/phase6_base64.zig`
- `zigux/tests/phase6_base64_c_parity.zig`
- `zigux/tests/phase6_base64_perf.zig`
- `zigux/tests/fixtures/phase6_base64_vectors.zig`
- `zigux/tests/fixtures/phase6_base64_c_harness.c`
- `scripts/zigux/check-phase6-base64-c-parity.py`
- `Documentation/zigux/phase6-base64-slice.md`
- the `base64` rows inside `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, and `zigux/tests/phase6_helper_parity_manifest.json`

Treat base64 fixture, direct parity, perf-threshold, or review-gate follow-ups as base64-owned work in Memory rather than reusing stale hard-coded lane labels in this shared note. When a later same-lane review needs only the shipped base64 packet, rerun the direct C parity spot check through `python3 scripts/zigux/check-phase6-base64-c-parity.py` and the helper-local slowdown gate through `make -C zigux phase6-base64-perf` instead of reopening the whole shared Phase 6 helper bundle by default.

### `P6-L09` bsearch packet

Keep helper-local work under:

- `lib/bsearch.zig`
- `zigux/tests/phase6_bsearch.zig`
- `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`
- `zigux/tests/phase6_bsearch_c_abi_budget.zig`
- `Documentation/zigux/phase6-bsearch-slice.md`
- the `bsearch` rows inside `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, and `zigux/tests/phase6_helper_parity_manifest.json`

Treat `P6-L09` as a closed legacy verification label only. New bsearch lower-bound, upper-bound, direct C ABI equality-budget, comparison-budget, or slice-note follow-ups stay bsearch-owned in Memory and should not reuse `P6-L09` as the packet-wide routing label. When a later same-lane review needs only the shipped bsearch packet, use `zig build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig` or `make -C zigux phase6-bsearch-test` so the focused helper rerun stays scoped to `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, and `zigux/tests/phase6_bsearch_c_abi_budget.zig` instead of reopening the whole shared Phase 6 bundle by default.

### checksum packet

Keep helper-local work under:

- `lib/checksum.zig`
- `zigux/tests/phase6_checksum.zig`
- `zigux/tests/phase6_checksum_perf.zig`
- `zigux/tests/phase6_checksum_c_parity.zig`
- `zigux/tests/fixtures/phase6_checksum_vectors.zig`
- `zigux/tests/fixtures/phase6_checksum_c_harness.c`
- `scripts/zigux/check-phase6-checksum-c-parity.py`
- `Documentation/zigux/phase6-checksum-slice.md`
- the `checksum` rows inside `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, and `zigux/tests/phase6_helper_parity_manifest.json`

Treat checksum note, count-correction, helper, or fixture follow-ups as checksum-owned work in Memory rather than reusing stale hard-coded lane labels in this shared note. When a later same-lane review needs only the shipped checksum packet, rerun the direct C parity replay through `python3 scripts/zigux/check-phase6-checksum-c-parity.py` and the helper-local slowdown gate through `make -C zigux phase6-checksum-perf` instead of reopening the whole shared Phase 6 helper bundle by default.

### hexdump packet

Keep helper-local work under:

- `lib/hexdump.zig`
- `zigux/tests/phase6_hexdump.zig`
- `zigux/tests/phase6_hexdump_perf.zig`
- `zigux/tests/fixtures/phase6_hexdump_vectors.zig`
- `Documentation/zigux/phase6-hexdump-slice.md`
- the `hexdump` rows inside `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, and `zigux/tests/phase6_helper_parity_manifest.json`

Treat hexdump row, threshold, or fixture follow-ups as hexdump-owned work in Memory rather than reusing stale hard-coded lane labels in this shared note. When a later same-lane review needs only the shipped hexdump packet, use `zig build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig` or `make -C zigux phase6-hexdump-test` for the focused helper replay and `make -C zigux phase6-hexdump-perf` for the dedicated slowdown gate instead of reopening the whole shared Phase 6 helper bundle by default.

## Anti-Overlap Rules

- Do not treat a shared file as shared-lane work when the diff only changes one helper row.
- If `zigux/tests/phase6_helper_parity_manifest.json` changes only one helper block under `helpers`, `perf_thresholds`, `fixture_posture`, or `determinism_evidence`, route that work back to the owning helper lane.
- If `Documentation/zigux/phase6-helper-parity-catalog.md` or `Documentation/zigux/phase6-perf-gate-survey.md` changes only one helper subsection, route that work back to the owning helper lane.
- Reopen this shared sequencing lane only when packet membership, shared routes, shared checker coverage, shared status wording, or helper-owner boundaries drift.
- If a shared route changes, update the shared note first, then let the owning helper lane repair only the helper-local evidence it actually owns.

## Current Bounded Next Step

Leave this lane parked unless a later Phase 6 run changes the shared `phase6` packet routing, the aggregate `phase6-perf` posture, the shared surface checker, or the owner split between the shared packet and the four helper packets. When that happens, keep the follow-up shared-surface-only and route helper-local evidence repairs back to the corresponding base64, bsearch, checksum, or hexdump packet in Memory rather than relying on stale lane ids recorded here.
