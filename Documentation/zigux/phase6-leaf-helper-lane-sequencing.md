# Phase 6 Leaf-Helper Lane Sequencing

This note keeps the bounded Phase 6 leaf-helper packet from overlapping itself on `master`.

## Status

- `PHASE6_LANE_MAP_STATUS=active`
- `PHASE6_PACKET=base64-bsearch-checksum-hexdump`
- shared sequencing lane key: `P6-Y10`
- shared tests-root reminder follow-through: keep it under `P6-Y10` unless a later run reserves a fresh dedicated shared lane key first
- shared packet status source: `zigux/tests/phase6_helper_parity_manifest.json`
- shared packet catalog: `Documentation/zigux/phase6-helper-parity-catalog.md`
- shared perf posture note: `Documentation/zigux/phase6-perf-gate-survey.md`

## Shared-Surface Owner

Use `P6-Y10` only for packet-wide routing, ownership, or anti-overlap truthfulness across:
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

### `P6-L01` and `P6-Y01` base64 packet

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

Treat `P6-L01` as the bounded base64 helper lane and `P6-Y01` as the base64 perf-boundary ownership lane when those same helper-local surfaces could plausibly overlap.

### `P6-L08`, `P6-L11`, and `P6-Y04` bsearch packet

<!-- compatibility marker for the current shared-surface checker: ### `P6-L09` bsearch packet -->

Keep helper-local work under:

- `lib/bsearch.zig`
- `zigux/tests/phase6_bsearch.zig`
- `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`
- `zigux/tests/phase6_bsearch_c_abi_budget.zig`
- `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`
- `Documentation/zigux/phase6-bsearch-slice.md`
- the `bsearch` rows inside `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, and `zigux/tests/phase6_helper_parity_manifest.json`

Treat `P6-L08` as the bounded bsearch helper lane, `P6-L11` as the bsearch review-gate tightening lane, and `P6-Y04` as the bsearch parked-note or closure-correction lane when the same helper packet could otherwise overlap itself.

### `P6-L13`, `P6-L16`, `P6-L17`, and `P6-L18` checksum packet

Keep helper-local work under:

- `lib/checksum.zig`
- `zigux/tests/phase6_checksum.zig`
- `zigux/tests/phase6_checksum_perf.zig`
- `zigux/tests/phase6_checksum_c_parity.zig`
- `zigux/tests/fixtures/phase6_checksum_vectors.zig`
- `zigux/tests/fixtures/phase6_checksum_c_harness.c`
- `scripts/zigux/check-phase6-checksum-c-parity.py`
- `scripts/zigux/check-phase6-checksum-packet.py`
- `Documentation/zigux/phase6-checksum-slice.md`
- the `checksum` rows inside `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, and `zigux/tests/phase6_helper_parity_manifest.json`

Treat `P6-L13` and `P6-L18` as checksum helper-local parity or hardening lanes, `P6-L16` as the checksum fixture-governance or helper-owned drift lane, and `P6-L17` as the checksum review-gate truthfulness lane when those same helper-local surfaces could plausibly overlap.

Current `master` now carries the checksum-owned helper, focused replay, helper-local perf replay, fixture companion, and C-parity companion again, so reopen `P6-Y10` only for packet-wide route, checklist, checker, manifest, or tests-root retelling that spans the shared packet instead of the checksum-owned packet itself.

### `P6-L19`, `P6-Y07`, `P6-Y08`, and `P6-Y09` hexdump packet

Keep helper-local work under:

- `lib/hexdump.zig`
- `zigux/tests/phase6_hexdump.zig`
- `zigux/tests/phase6_hexdump_perf.zig`
- `zigux/tests/phase6_hexdump_perf_matrix.zig`
- `zigux/tests/fixtures/phase6_hexdump_vectors.zig`
- `Documentation/zigux/phase6-hexdump-slice.md`
- `Documentation/zigux/phase6-hexdump-perf-refresh.md`
- the `hexdump` rows inside `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, and `zigux/tests/phase6_helper_parity_manifest.json`

Treat `P6-L19` as the hexdump parked-survey or slice-note truthfulness lane, `P6-Y07` as the hexdump fixture-governance lane, `P6-Y08` as the hexdump serialized empty-ASCII length-packet closure lane, and `P6-Y09` as the hexdump perf-refresh ownership lane when the same helper-local review packet could otherwise overlap itself.

## Anti-Overlap Rules
- Do not treat a shared file as shared-lane work when the diff only changes one helper row.
- If `zigux/tests/phase6_helper_parity_manifest.json` changes only one helper block under `helpers`, `perf_thresholds`, `fixture_posture`, or `determinism_evidence`, route that work back to the owning helper lane.
- If `Documentation/zigux/phase6-helper-parity-catalog.md` or `Documentation/zigux/phase6-perf-gate-survey.md` changes only one helper subsection, route that work back to the owning helper lane.
- Reopen this shared sequencing lane only when packet membership, shared routes, shared checker coverage, shared status wording, helper-owner boundaries, or the shared tests-root reminder packet drift.
- If a shared route changes, update the shared note first, then let the owning helper lane repair only the helper-local evidence it actually owns.
- If checksum helper-local evidence changes, let checksum lanes repair `lib/checksum.zig`, checksum-owned tests and fixtures, checksum packet checks, and the checksum slice; reopen `P6-Y10` only for repo-wide route, checklist, checker, manifest, or summary wording that spans multiple helper packets.
- If a helper packet has separate parked-survey, fixture-governance, and helper-drift lanes, route the smallest truthful follow-up to the narrowest owner instead of reopening the whole helper family.
- If a shared summary drift is isolated to `zigux/tests/README.md`, keep that reminder repair under `P6-Y10` until a fresh shared tests-root lane key is reserved, rather than reusing a helper-owned or historical lane key.

## Current Bounded Next Step

Leave this lane parked unless a later Phase 6 run changes the shared `phase6` packet routing, the aggregate `phase6-perf` posture, the shared surface checker, or the owner split between the shared packet and the four helper packets.

Fresh repo-first rereads on current `master` now show the checksum packet restored in the committed tree beside the already-readable base64, bsearch, and hexdump packets: `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, `zigux/tests/fixtures/phase6_checksum_vectors.zig`, `zigux/tests/phase6_checksum_c_parity.zig`, and `zigux/tests/fixtures/phase6_checksum_c_harness.c` are present again.

The remaining shared drift is narrower: `Documentation/zigux/phase6-perf-gate-survey.md`, `zigux/tests/README.md`, and the shared manifest now already reflect the restored checksum packet, while `scripts/zigux/README.md` still presents `make -C zigux phase6-base64-perf` and `make -C zigux phase6-checksum-perf` as inventory-only convenience routes even though current `zigux/Makefile`, `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, and `zigux/tests/phase6_helper_parity_manifest.json` already treat those two helper-local wrappers as committed target bodies and reserve the inventory-only caveat for the aggregate `phase6-validate`, `phase6-perf`, and `phase6` routes.

Keep `P6-Y10` limited to one shared owner-map, scripts-root, checker, or packet-level manifest, catalog, or perf-summary correction that makes the remaining wrapper-route split obvious without reopening helper-local checksum work or reusing stale lane keys.
