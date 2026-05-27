# Phase 6 Helper Evidence Catalog

This note records the current helper-evidence survey for the bounded Phase 6 leaf-helper packet on `master`.

- surveyed head: `current-master-readback-2026-05-22`
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

## Current direct-readback posture

Authenticated current-master rereads already recovered `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, `scripts/zigux/check-phase6-base64-c-parity.py`, and `Documentation/zigux/phase6-perf-gate-survey.md` inside the broader base64 parity packet.

A targeted authenticated current-master reread on 2026-05-27 also directly recovered `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig` and `zigux/tests/phase6_base64_c_casegen.zig`, so the Phase 6 base64 packet no longer carries a known direct-readback generator gap.

The directly readable shared packet in this environment is therefore this helper-evidence catalog together with `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, `Documentation/zigux/phase6-runtime-command-environment-gap-survey.md`, `Documentation/zigux/phase6-hexdump-slice.md`, `Documentation/zigux/phase6-hexdump-perf-refresh.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/README.md`, `zigux/Makefile`, `zigux/tests/phase6_build.zig`, `zigux/tests/phase6_helper_evidence_manifest.json`, `zigux/tests/phase6_helper_parity_manifest.json`, `scripts/zigux/check-phase6-present-entrypoints.py`, `scripts/zigux/check-phase6-base64-bsearch-perf-markers.py`, `scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py`, `scripts/zigux/check-phase6-perf-threshold-markers.py`, `scripts/zigux/check-phase6-hexdump-packet.py`, and `scripts/zigux/check-phase6-hexdump-route.py`.

Keep `Documentation/zigux/phase6-runtime-command-environment-gap-survey.md` inside that directly readable shared packet as the control-surface boundary note that stops the helper-only Phase 6 packet from implying shell, TTY, runtime-session, or persisted-environment ownership.

The docs-root README now keeps a dedicated Phase 6 helper-evidence stanza aligned with surveyed head `current-master-readback-2026-05-22`, so keep `Documentation/zigux/README.md` inside the current direct-readback packet rather than treating it as a remaining shared-note follow-through gap.

The broader shared perf survey is directly readable again and now matches the current directly readable helper-local packet for `base64`, `bsearch`, `checksum`, and `hexdump`. Authenticated current-master rereads now directly recover `Documentation/zigux/phase6-perf-gate-survey.md`, and that broader perf note is now aligned again on the currently readable base64, bsearch, checksum, and hexdump measurement packet. Treat the remaining shared perf-note risk as ordinary future truthfulness drift rather than a current helper-local measurement gap, and keep the directly readable helper-evidence packet above as the authenticated source of truth in this runtime.

## Current helper-evidence rows

### base64

- roadmap anchor: `lib/base64.c`
- Zig helper: `lib/base64.zig`
- focused helper replay: `zigux/tests/phase6_base64.zig`
- dedicated slowdown replay: `zigux/tests/phase6_base64_perf.zig`
- committed fixture surface: `zigux/tests/fixtures/phase6_base64_vectors.zig`
- focused direct C parity replay: `zigux/tests/phase6_base64_c_parity.zig`
- direct C parity harness: `zigux/tests/fixtures/phase6_base64_c_harness.c`
- generator-side direct C parity companions: `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig` and `zigux/tests/phase6_base64_c_casegen.zig`
- dedicated corpus checker: `scripts/zigux/check-phase6-base64-corpus-determinism.py`
- direct C parity checker: `scripts/zigux/check-phase6-base64-c-parity.py`
- slice note: `Documentation/zigux/phase6-base64-slice.md`
- current review posture: the roadmap-backed base64 packet now has directly readable helper-local evidence through `lib/base64.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_base64_perf.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, `scripts/zigux/check-phase6-base64-corpus-determinism.py`, `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig`, `zigux/tests/phase6_base64_c_casegen.zig`, `scripts/zigux/check-phase6-base64-c-parity.py`, `Documentation/zigux/phase6-base64-slice.md`, this shared catalog, `zigux/tests/phase6_helper_evidence_manifest.json`, the returned `zigux/tests/phase6_helper_parity_manifest.json`, the restored shared build foothold, the current Makefile wrapper surface, and the directly readable scripts-root plus tests-root reminders

### bsearch

- roadmap anchor: `lib/bsearch.c`
- Zig helper: `lib/bsearch.zig`
- focused helper replay: `zigux/tests/phase6_bsearch.zig`
- dedicated slowdown replay: `zigux/tests/phase6_bsearch_perf.zig`
- focused C ABI replays: `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig` and `zigux/tests/phase6_bsearch_c_abi_budget.zig`
- direct C parity companions: `zigux/tests/phase6_bsearch_c_parity.zig`, `zigux/tests/fixtures/phase6_bsearch_c_harness.c`, and `scripts/zigux/check-phase6-bsearch-c-parity.py`
- compact shared seed fixture companion: `zigux/tests/fixtures/phase6_bsearch_vectors.zig`
- dedicated corpus checker: `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`
- slice note: `Documentation/zigux/phase6-bsearch-slice.md`
- current review posture: direct helper-local evidence is readable again through `lib/bsearch.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_bsearch_perf.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, `zigux/tests/phase6_bsearch_c_abi_budget.zig`, `zigux/tests/phase6_bsearch_c_parity.zig`, `zigux/tests/fixtures/phase6_bsearch_c_harness.c`, `zigux/tests/fixtures/phase6_bsearch_vectors.zig`, `Documentation/zigux/phase6-bsearch-slice.md`, `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`, `scripts/zigux/check-phase6-bsearch-c-parity.py`, this shared catalog, `zigux/tests/phase6_helper_evidence_manifest.json`, the returned `zigux/tests/phase6_helper_parity_manifest.json`, the restored shared build foothold, the current Makefile wrapper surface, and the directly readable scripts-root plus tests-root reminders; the direct C parity spot check now keeps 17 sorted lookup cases explicit across ascending and descending comparator-driven lookups, duplicate hits, heterogeneous string-key lookup, and mutable write-through behavior

### checksum

- roadmap anchor: `lib/checksum.c`
- Zig helper: `lib/checksum.zig`
- focused helper replay: `zigux/tests/phase6_checksum.zig`
- dedicated slowdown replay: `zigux/tests/phase6_checksum_perf.zig`
- committed fixture surface: `zigux/tests/fixtures/phase6_checksum_vectors.zig`
- dedicated corpus checker: `scripts/zigux/check-phase6-checksum-corpus-evidence.py`
- direct C parity companions: `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`
- slice note: `Documentation/zigux/phase6-checksum-slice.md`
- current review posture: direct helper-local evidence is readable again through `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, `zigux/tests/fixtures/phase6_checksum_vectors.zig`, `scripts/zigux/check-phase6-checksum-corpus-evidence.py`, `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, `scripts/zigux/check-phase6-checksum-c-parity.py`, `Documentation/zigux/phase6-checksum-slice.md`, this shared catalog, `zigux/tests/phase6_helper_evidence_manifest.json`, the returned `zigux/tests/phase6_helper_parity_manifest.json`, the restored shared build foothold, the current Makefile wrapper surface, and the directly readable scripts-root plus tests-root reminders, and the current perf packet now keeps both the payload slowdown matrix and the `checksum.ipFastCsum` IPv4 fast-path matrix explicit through `zigux/tests/phase6_checksum_perf.zig`, `zigux/tests/fixtures/phase6_checksum_vectors.zig`, `zig build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig`, `make -C zigux phase6-checksum-perf-matrix-test`, `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`, `make -C zigux phase6-checksum-perf`, and `make -C zigux phase6-perf`

### hexdump

- roadmap anchor: `lib/hexdump.c`
- Zig helper: `lib/hexdump.zig`
- focused helper replay: `zigux/tests/phase6_hexdump.zig`
- dedicated slowdown replay: `zigux/tests/phase6_hexdump_perf.zig`
- exact perf-matrix preflight: `zigux/tests/phase6_hexdump_perf_matrix.zig`
- committed fixture surface: `zigux/tests/fixtures/phase6_hexdump_vectors.zig`
- helper-local packet checker: `scripts/zigux/check-phase6-hexdump-packet.py`
- route checker: `scripts/zigux/check-phase6-hexdump-route.py`
- perf refresh note: `Documentation/zigux/phase6-hexdump-perf-refresh.md`
- slice note: `Documentation/zigux/phase6-hexdump-slice.md`
- current review posture: direct helper-local evidence is readable again through `lib/hexdump.zig`, `zigux/tests/phase6_hexdump.zig`, `zigux/tests/phase6_hexdump_perf.zig`, `zigux/tests/phase6_hexdump_perf_matrix.zig`, `zigux/tests/fixtures/phase6_hexdump_vectors.zig`, `scripts/zigux/check-phase6-hexdump-packet.py`, `scripts/zigux/check-phase6-hexdump-route.py`, `Documentation/zigux/phase6-hexdump-perf-refresh.md`, `Documentation/zigux/phase6-hexdump-slice.md`, this shared catalog, `zigux/tests/phase6_helper_evidence_manifest.json`, the returned `zigux/tests/phase6_helper_parity_manifest.json`, the restored shared build foothold, the current Makefile wrapper surface, and the directly readable scripts-root plus tests-root reminders

## Roadmap perf-gap readback

The Phase 6 roadmap requires perf gates for math-sensitive helpers across the bounded `lib/base64.c`, `lib/bsearch.c`, `lib/checksum.c`, and `lib/hexdump.c` packet. Current direct-readback measurement coverage is now present for each helper, even though the replay shape is still intentionally lightweight rather than a cross-machine benchmark suite:

- `base64` keeps a dedicated helper-local slowdown replay in `zigux/tests/phase6_base64_perf.zig`, and `zigux/tests/fixtures/phase6_base64_vectors.zig` still centralizes six fixture-owned encode and decode cases across standard, URL-safe, and IMAP variants.
- `bsearch` now keeps a dedicated helper-local perf replay in `zigux/tests/phase6_bsearch_perf.zig`, and `zigux/tests/fixtures/phase6_bsearch_vectors.zig` still centralizes the representative `len15`, `len64`, and `len1024` perf cases together with deterministic seeded hit and miss queries that keep average and worst-case comparator work inside the current binary-search budget. The direct C parity spot check in `zigux/tests/phase6_bsearch_c_parity.zig`, `zigux/tests/fixtures/phase6_bsearch_c_harness.c`, and `scripts/zigux/check-phase6-bsearch-c-parity.py` now keeps 17 sorted lookup cases explicit across ascending and descending comparator-driven lookups, duplicate hits, heterogeneous string-key lookup, and mutable write-through behavior.
- `checksum` keeps a dedicated helper-vs-reference slowdown gate in `zigux/tests/phase6_checksum_perf.zig`, with the committed payload threshold matrix (`64B`, `1501B`) and the `checksum.ipFastCsum` IPv4 fast-path matrix (`IPV4_20B`, `IPV4_20B_UPDATED`, `IPV4_24B`, `IPV4_60B`) still owned by `zigux/tests/fixtures/phase6_checksum_vectors.zig`; the shared replay packet exposes that packet through `zig build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig`, `make -C zigux phase6-checksum-perf-matrix-test`, `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`, `make -C zigux phase6-checksum-perf`, and `make -C zigux phase6-perf`.
- `hexdump` keeps a dedicated slowdown gate in `zigux/tests/phase6_hexdump_perf.zig`, with the current fixture matrix in `zigux/tests/fixtures/phase6_hexdump_vectors.zig` still covering four formatting cases from `16B-plain-g1` through `16B-ascii-g8`, and the restored rationale pair `Documentation/zigux/phase6-hexdump-slice.md` plus `Documentation/zigux/phase6-hexdump-perf-refresh.md` now makes that grouped-threshold packet reviewable again through the shared route guards.
- the remaining roadmap-aligned measurement risk is ordinary future drift between this catalog, `Documentation/zigux/phase6-perf-gate-survey.md`, the helper-local fixtures and perf harnesses, the aggregate `phase6-perf` wrapper, and the checker-backed manifest packet, not missing helper-local threshold ownership.

## Current shared replay inventory

- `zig build phase6-base64-test --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6-base64-test`
- `zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6-base64-perf`
- `python3 scripts/zigux/check-phase6-base64-c-parity.py`
- `zig build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6-bsearch-test`
- `zig build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6-bsearch-perf`
- `python3 scripts/zigux/check-phase6-bsearch-c-parity.py`
- `python3 scripts/zigux/check-phase6-base64-bsearch-perf-markers.py`
- `zig build phase6-checksum-test --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6-checksum-test`
- `zig build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6-checksum-perf-matrix-test`
- `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6-checksum-perf`
- `python3 scripts/zigux/check-phase6-checksum-c-parity.py`
- `python3 scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py`
- `python3 scripts/zigux/check-phase6-perf-threshold-markers.py`
- `python3 scripts/zigux/check-phase6-hexdump-packet.py`
- `python3 scripts/zigux/check-phase6-hexdump-route.py`
- `zig build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6-hexdump-review`
- `zig build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6-hexdump-perf-matrix-test`
- `zig build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6-hexdump-test`
- `zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe`
- `make -C zigux phase6-hexdump-perf`
- `make -C zigux phase6-perf`

Reopen this catalog only when one of the four roadmap anchors gains or loses a truthful helper-evidence row on `master`.
