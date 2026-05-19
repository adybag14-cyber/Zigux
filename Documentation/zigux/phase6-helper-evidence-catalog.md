# Phase 6 Helper Evidence Catalog

This note records the current helper-evidence survey for the bounded Phase 6 leaf-helper packet on `master`.

- surveyed head: `61e026c`
- lane scope: shared helper-evidence rows and machine-readable manifest only
- shared scripts-root reminder: `scripts/zigux/README.md`
- shared tests-root reminder: `zigux/tests/README.md`
- shared docs-root reminder: `Documentation/zigux/README.md`
- directly readable shared build foothold: `zigux/tests/phase6_build.zig`
- directly readable shared Makefile wrapper surface: `zigux/Makefile`
- shared machine-readable manifest: `zigux/tests/phase6_helper_evidence_manifest.json`
- returned helper-parity companion: `zigux/tests/phase6_helper_parity_manifest.json`
- roadmap-backed helper anchors:
  - `lib/base64.c`
  - `lib/bsearch.c`
  - `lib/checksum.c`
  - `lib/hexdump.c`

## Why this catalog exists

The four Phase 6 slice notes keep the helper-local detail, but they do not keep one small shared table of the roadmap anchor, the landed Zig helper, and the current reviewable evidence row. This catalog closes that narrower review gap without widening the Phase 6 packet into new perf policy, validator, or helper-semantic work.

## Current direct-readback warning

Fresh direct GitHub contents reads on current `master` still return missing for several shared-note and helper-local packet members that older Phase 6 reminder surfaces have treated as shipped evidence, including:

- `Documentation/zigux/phase6-helper-parity-catalog.md`
- `Documentation/zigux/phase6-perf-gate-survey.md`
- `Documentation/zigux/phase6-hexdump-slice.md`
- `Documentation/zigux/phase6-hexdump-perf-refresh.md`
- `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig`
- `zigux/tests/phase6_base64_c_parity.zig`
- `zigux/tests/phase6_base64_c_casegen.zig`
- `zigux/tests/fixtures/phase6_base64_c_harness.c`
- `zigux/tests/phase6_checksum_c_parity.zig`
- `zigux/tests/fixtures/phase6_checksum_c_harness.c`
- `scripts/zigux/check-phase6-base64-c-parity.py`
- `scripts/zigux/check-phase6-checksum-c-parity.py`

Treat those paths as last-known Phase 6 packet members that require fresh reread or re-materialization before they are presented as current shipped direct evidence again. The directly readable shared packet in this environment is therefore this helper-evidence catalog together with `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, `zigux/tests/phase6_build.zig`, `zigux/tests/phase6_helper_evidence_manifest.json`, `zigux/tests/phase6_helper_parity_manifest.json`, and `scripts/zigux/check-phase6-present-entrypoints.py`.

Authenticated direct readback still leaves `Documentation/zigux/phase6-perf-gate-survey.md` missing on current `master`, so the remaining shared perf-note risk is reminder-surface drift rather than an executable-route gap: the directly readable helper-evidence packet already materializes `zigux/Makefile` with the current `phase6-base64-test`, `phase6-base64-perf`, `phase6-bsearch-test`, `phase6-checksum-test`, `phase6-checksum-perf`, `phase6-hexdump-review`, `phase6-hexdump-perf-matrix-test`, `phase6-hexdump-test`, and `phase6-hexdump-perf` wrapper targets, and it also materializes the narrower helper-parity companion `zigux/tests/phase6_helper_parity_manifest.json`.

## Current helper-evidence rows

### base64

- roadmap anchor: `lib/base64.c`
- Zig helper: `lib/base64.zig`
- focused helper replay: `zigux/tests/phase6_base64.zig`
- dedicated slowdown replay: `zigux/tests/phase6_base64_perf.zig`
- committed fixture surface: `zigux/tests/fixtures/phase6_base64_vectors.zig`
- last-known direct C parity companions still needing fresh direct reads: `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig`, `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/phase6_base64_c_casegen.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`
- slice note: `Documentation/zigux/phase6-base64-slice.md`
- current review posture: the roadmap-backed base64 packet now has directly readable helper-local evidence through `lib/base64.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_base64_perf.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, `Documentation/zigux/phase6-base64-slice.md`, this shared catalog, `zigux/tests/phase6_helper_evidence_manifest.json`, the returned `zigux/tests/phase6_helper_parity_manifest.json`, the restored shared build foothold, the current Makefile wrapper surface, and the directly readable scripts-root plus tests-root reminders, while the direct C parity companions still need fresh direct reads before they are presented as current shipped evidence

### bsearch

- roadmap anchor: `lib/bsearch.c`
- Zig helper: `lib/bsearch.zig`
- focused helper replay: `zigux/tests/phase6_bsearch.zig`
- focused C ABI replays: `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig` and `zigux/tests/phase6_bsearch_c_abi_budget.zig`
- compact shared seed fixture companion: `zigux/tests/fixtures/phase6_bsearch_vectors.zig`
- dedicated corpus checker: `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`
- slice note: `Documentation/zigux/phase6-bsearch-slice.md`
- current review posture: direct helper-local evidence is readable again through `lib/bsearch.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, `zigux/tests/phase6_bsearch_c_abi_budget.zig`, `zigux/tests/fixtures/phase6_bsearch_vectors.zig`, `Documentation/zigux/phase6-bsearch-slice.md`, `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`, this shared catalog, `zigux/tests/phase6_helper_evidence_manifest.json`, the returned `zigux/tests/phase6_helper_parity_manifest.json`, the restored shared build foothold, the current Makefile wrapper surface, and the directly readable scripts-root plus tests-root reminders

### checksum

- roadmap anchor: `lib/checksum.c`
- Zig helper: `lib/checksum.zig`
- focused helper replay: `zigux/tests/phase6_checksum.zig`
- dedicated slowdown replay: `zigux/tests/phase6_checksum_perf.zig`
- committed fixture surface: `zigux/tests/fixtures/phase6_checksum_vectors.zig`
- last-known direct C parity companions still needing fresh direct reads: `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`
- slice note: `Documentation/zigux/phase6-checksum-slice.md`
- current review posture: direct helper-local evidence is readable again through `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, `zigux/tests/fixtures/phase6_checksum_vectors.zig`, `Documentation/zigux/phase6-checksum-slice.md`, this shared catalog, `zigux/tests/phase6_helper_evidence_manifest.json`, the returned `zigux/tests/phase6_helper_parity_manifest.json`, the restored shared build foothold, the current Makefile wrapper surface, and the directly readable scripts-root plus tests-root reminders, while the direct C parity companions still need fresh direct reads before they are presented as current shipped evidence

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
- current review posture: direct helper-local evidence is readable again through `lib/hexdump.zig`, `zigux/tests/phase6_hexdump.zig`, `zigux/tests/phase6_hexdump_perf.zig`, `zigux/tests/phase6_hexdump_perf_matrix.zig`, `zigux/tests/fixtures/phase6_hexdump_vectors.zig`, `scripts/zigux/check-phase6-hexdump-packet.py`, this shared catalog, `zigux/tests/phase6_helper_evidence_manifest.json`, the returned `zigux/tests/phase6_helper_parity_manifest.json`, the restored shared build foothold, the current Makefile wrapper surface, and the directly readable scripts-root plus tests-root reminders, while the slice note and perf refresh note still need fresh direct reads before they are presented as current shipped evidence

## Roadmap perf-gap readback

The Phase 6 roadmap requires perf gates for math-sensitive helpers across the bounded `lib/base64.c`, `lib/bsearch.c`, `lib/checksum.c`, and `lib/hexdump.c` packet. Current direct-readback measurement coverage on surveyed head `61e026c` is therefore mixed rather than uniform:

- `base64` keeps a dedicated helper-local slowdown replay in `zigux/tests/phase6_base64_perf.zig`, and `zigux/tests/fixtures/phase6_base64_vectors.zig` still centralizes six fixture-owned encode and decode cases across standard, URL-safe, and IMAP variants.
- `checksum` keeps a dedicated helper-vs-reference slowdown gate in `zigux/tests/phase6_checksum_perf.zig`, with the committed `64B` and `1501B` threshold matrix still owned by `zigux/tests/fixtures/phase6_checksum_vectors.zig`.
- `hexdump` keeps a dedicated slowdown gate in `zigux/tests/phase6_hexdump_perf.zig`, with the current fixture matrix in `zigux/tests/fixtures/phase6_hexdump_vectors.zig` still covering four formatting cases from `16B-plain-g1` through `16B-ascii-g8`.
- `bsearch` still measures bounded search cost through `zigux/tests/phase6_bsearch_c_abi_budget.zig`, `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`, and the deterministic `perf_cases` plus seeded query corpus in `zigux/tests/fixtures/phase6_bsearch_vectors.zig`, which hold raw C ABI search and equal-range comparisons to logarithmic budgets across representative lengths instead of using a dedicated wall-clock slowdown harness.
- the remaining roadmap-aligned measurement gap is shared survey truthfulness rather than new helper semantics: `Documentation/zigux/phase6-perf-gate-survey.md` is still missing on current `master`, so the directly readable helper-evidence packet should stay anchored to the returned `zigux/tests/phase6_helper_parity_manifest.json`, the directly readable `zigux/Makefile` Phase 6 wrapper targets, the dedicated `phase6-hexdump-perf-matrix-test` preflight route, and the returned helper-local hexdump packet checker while `bsearch` continues to measure bounded search cost through its C ABI budget route instead of a dedicated slowdown replay comparable to the base64, checksum, and hexdump helper-local gates.

## Current shared replay inventory

- `zig build phase6-base64-test --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6-base64-test`
- `zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6-base64-perf`
- `zig build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6-bsearch-test`
- `zig build phase6-checksum-test --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6-checksum-test`
- `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6-checksum-perf`
- `python3 scripts/zigux/check-phase6-hexdump-packet.py`
- `python3 scripts/zigux/check-phase6-hexdump-route.py`
- `zig build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6-hexdump-review`
- `zig build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6-hexdump-perf-matrix-test`
- `zig build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6-hexdump-test`
- `zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6-hexdump-perf`

Reopen this catalog only when one of the four roadmap anchors gains or loses a truthful helper-evidence row on `master`.
