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

### `P6-L04` base64 packet

Keep helper-local work under:

- `lib/base64.zig`
- `zigux/tests/phase6_base64.zig`
- `zigux/tests/phase6_base64_perf.zig`
- `zigux/tests/fixtures/phase6_base64_vectors.zig`
- `Documentation/zigux/phase6-base64-slice.md`
- the `base64` rows inside `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, and `zigux/tests/phase6_helper_parity_manifest.json`

### `P6-L09` bsearch packet

Keep helper-local work under:

- `lib/bsearch.zig`
- `zigux/tests/phase6_bsearch.zig`
- `Documentation/zigux/phase6-bsearch-slice.md`
- the `bsearch` rows inside `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, and `zigux/tests/phase6_helper_parity_manifest.json`

### `P6-Y06` and `P6-L16` checksum packet

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

Treat `P6-Y06` as the checksum note or count-correction lane and `P6-L16` as the checksum helper-or-fixture drift lane when both could plausibly touch the same helper packet.

### `P6-Y08` hexdump packet

Keep helper-local work under:

- `lib/hexdump.zig`
- `zigux/tests/phase6_hexdump.zig`
- `zigux/tests/phase6_hexdump_perf.zig`
- `zigux/tests/fixtures/phase6_hexdump_vectors.zig`
- `Documentation/zigux/phase6-hexdump-slice.md`
- the `hexdump` rows inside `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, and `zigux/tests/phase6_helper_parity_manifest.json`

## Anti-Overlap Rules

- Do not treat a shared file as shared-lane work when the diff only changes one helper row.
- If `zigux/tests/phase6_helper_parity_manifest.json` changes only one helper block under `helpers`, `perf_thresholds`, `fixture_posture`, or `determinism_evidence`, route that work back to the owning helper lane.
- If `Documentation/zigux/phase6-helper-parity-catalog.md` or `Documentation/zigux/phase6-perf-gate-survey.md` changes only one helper subsection, route that work back to the owning helper lane.
- Reopen this shared sequencing lane only when packet membership, shared routes, shared checker coverage, shared status wording, or helper-owner boundaries drift.
- If a shared route changes, update the shared note first, then let the owning helper lane repair only the helper-local evidence it actually owns.

## Current Bounded Next Step

Leave this lane parked unless a later Phase 6 run changes the shared `phase6` packet routing, the aggregate `phase6-perf` posture, the shared surface checker, or the owner split between the shared packet and the four helper packets. When that happens, keep the follow-up shared-surface-only and route helper-local evidence repairs back to `P6-L04`, `P6-L09`, `P6-Y06` or `P6-L16`, and `P6-Y08`.
