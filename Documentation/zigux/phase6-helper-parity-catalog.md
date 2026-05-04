# Phase 6 Helper Parity Catalog

This note records the current shared Phase 6 leaf-helper evidence bundle at the inspected `master` tip when this catalog was refreshed.

- verified head: `11ce68dddd5ecc31de988f3d8bf6e4c680be04b0`
- machine-readable inventory: `zigux/tests/phase6_helper_parity_manifest.json`
- shared packet posture: parked after the current helper-local parity and perf surface cleared the bounded Phase 6 goal

## Scope

The current Phase 6 helper-parity packet is intentionally limited to the four roadmap-backed leaf helpers:

- `lib/base64.zig`
- `lib/bsearch.zig`
- `lib/checksum.zig`
- `lib/hexdump.zig`

The shared replay and gating surface for that packet is:

- `zigux/tests/phase6_build.zig`
- `zigux/Makefile`
- `scripts/zigux/validate-phase6.py`
- `.github/workflows/zigux-bootstrap.yml`
- `Documentation/zigux/README.md`
- `Documentation/zigux/phase6-helper-parity-catalog.md`
- `Documentation/zigux/phase6-perf-gate-survey.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `zigux/tests/phase6_helper_parity_manifest.json`

This shared catalog exists so reviewers can confirm, in one place, that the roadmap-backed Phase 6 packet still stops at the four leaf helpers and that the docs, validator, workflow, perf-gate survey, and test entrypoints all describe the same shipped surface. The manifest is the compact machine-readable companion for that same packet, while this note keeps the reviewer-facing perf and fixture posture explicit. The per-helper evidence blocks below also map each Zig port back to its exact Linux roadmap anchor so the shared survey does not drift into a Zig-only reading of the tranche.

## Current helper evidence

### base64

- roadmap anchor: `lib/base64.c`
- helper: `lib/base64.zig`
- tests: `zigux/tests/phase6_base64.zig`
- perf: `zigux/tests/phase6_base64_perf.zig`
- external parity: `scripts/zigux/check-phase6-base64-c-parity.py`
- external parity harnesses: `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/phase6_base64_c_casegen.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`
- fixtures: `zigux/tests/fixtures/phase6_base64_vectors.zig`
- slice note: `Documentation/zigux/phase6-base64-slice.md`

### bsearch

- roadmap anchor: `lib/bsearch.c`
- helper: `lib/bsearch.zig`
- tests: `zigux/tests/phase6_bsearch.zig`
- shared portability coverage: `zigux/tests/phase6_bsearch.zig` now exercises both typed and raw runtime-selected comparator pointers across native and C ABI paths
- perf: `zigux/tests/phase6_bsearch_perf.zig`
- perf corpus fixture: `zigux/tests/fixtures/phase6_bsearch_vectors.zig`
- external parity: `scripts/zigux/check-phase6-bsearch-c-parity.py`
- external parity runner: `zigux/tests/phase6_bsearch_c_parity.zig`
- external parity harness: `zigux/tests/fixtures/phase6_bsearch_c_harness.c`
- slice note: `Documentation/zigux/phase6-bsearch-slice.md`

### checksum

- roadmap anchor: `lib/checksum.c`
- helper: `lib/checksum.zig`
- tests: `zigux/tests/phase6_checksum.zig`
- perf: `zigux/tests/phase6_checksum_perf.zig`
- external parity: `scripts/zigux/check-phase6-checksum-c-parity.py`
- external parity runner: `zigux/tests/phase6_checksum_c_parity.zig`
- external parity harness: `zigux/tests/fixtures/phase6_checksum_c_harness.c`
- fixtures: `zigux/tests/fixtures/phase6_checksum_vectors.zig`
- slice note: `Documentation/zigux/phase6-checksum-slice.md`

### hexdump

- roadmap anchor: `lib/hexdump.c`
- helper: `lib/hexdump.zig`
- tests: `zigux/tests/phase6_hexdump.zig`
- perf: `zigux/tests/phase6_hexdump_perf.zig`
- external parity: `scripts/zigux/check-phase6-hexdump-c-parity.py`
- external parity runner: `zigux/tests/phase6_hexdump_c_parity.zig`
- external parity harness: `zigux/tests/fixtures/phase6_hexdump_c_harness.c`
- fixtures: `zigux/tests/fixtures/phase6_hexdump_vectors.zig`
- slice note: `Documentation/zigux/phase6-hexdump-slice.md`

## Current perf gate posture

The current Phase 6 perf packet is intentionally mixed. Three helpers now carry fixture-backed relative slowdown thresholds, and one helper carries an algorithmic comparison-budget threshold rather than a nanosecond ceiling.

### base64

- `zigux/tests/phase6_base64_perf.zig` replays two deterministic payloads: `64B` at `20_000` reps and `1KB` at `4_000` reps.
- the current numeric thresholds are `max_encode_slowdown_pct = 190` and `max_decode_slowdown_pct = 320` for all ten replay cases: padded standard `64B` and `1KB`, padded plus unpadded URL-safe `64B` and `1KB`, and padded plus unpadded IMAP `64B` and `1KB`.
- the harness measures those cases against the padded `std.base64.standard` reference path, the padded and unpadded `std.base64.url_safe{,_no_pad}` reference paths, and translated padded plus unpadded standard-to-IMAP reference paths for the IMAP alphabet.
- the harness also rechecks encode parity, decode parity, and round-trip correctness before and after the timed loops while reporting helper and reference nanoseconds per operation plus the observed median-of-three slowdown percentages.

### bsearch

- `zigux/tests/phase6_bsearch_perf.zig` replays three representative sorted slices: `256` entries at `2_000` reps, `4096` entries at `500` reps, and `65536` entries at `64` reps.
- the machine-checked threshold is algorithmic rather than time-based: every replayed lookup must stay within `std.math.log2_int_ceil(len) + 1` comparator calls, and the run still requires `avg_compare_calls <= std.math.log2_int_ceil(len) + 1`.
- the query corpus is deterministic by construction: each replay starts with fixed edge, midpoint, and miss probes before the remaining seeded interior lookups exercise the average-path budget.
- the harness still prints `ns_per_lookup`, but no stable nanosecond ceiling is claimed today.

### checksum

- `zigux/tests/phase6_checksum_perf.zig` replays two deterministic payloads from `zigux/tests/fixtures/phase6_checksum_vectors.zig`: `64` bytes at `20_000` reps and `1501` bytes at `4_000` reps.
- the current numeric threshold is `max_slowdown_pct = 150` for both fixture cases, checked against the widened-accumulator `referencePartial` path.
- the harness also records helper and reference nanoseconds per call, helper and reference nanoseconds per byte, the observed `slowdown_pct`, and the folded checksum result.

### hexdump

- `zigux/tests/phase6_hexdump_perf.zig` now replays four deterministic formatter cases from `zigux/tests/fixtures/phase6_hexdump_vectors.zig`: `16B-plain` at `40_000` reps, `32B-ascii-g2` at `10_000` reps, `16B-ascii-g4` at `20_000` reps, and `16B-ascii-g8` at `20_000` reps.
- the current numeric thresholds keep `16B-plain` at `max_slowdown_pct = 175` while the grouped ASCII `32B-ascii-g2` and `16B-ascii-g4` replays stay at `max_slowdown_pct = 550` and the wider native-endian `16B-ascii-g8` replay uses `max_slowdown_pct = 600`, checked against the committed `fixtures.prepareExpectedLine(...)` reference path.
- the harness also records helper and reference nanoseconds per call, helper and reference nanoseconds per byte, the observed `slowdown_pct`, and the required formatted line length.

## Current fixture corpus determinism

The committed Phase 6 fixture corpus is deterministic today because every shipped helper replay hangs off committed literals or sorted parity output instead of generated snapshot files.

- `zigux/tests/fixtures/phase6_base64_vectors.zig` is the current static base64 corpus with 22 standard encode vectors, 30 variant encode vectors, 22 standard decode vectors, 20 variant decode vectors, 28 invalid decode vectors, 2 committed perf payload cases, and 10 committed perf replay cases, including a repeated-alternate-alphabet multi-quartet sample family for the URL-safe and IMAP branches plus padded malformed tail-bit rejects across the standard, URL-safe, and IMAP variants.
- `zigux/tests/fixtures/phase6_base64_c_harness.c`, `zigux/tests/phase6_base64_c_casegen.zig`, and `zigux/tests/phase6_base64_c_parity.zig` replay that same representative base64 surface through `python3 scripts/zigux/check-phase6-base64-c-parity.py`; the built-in `--self-test` path now reports `PHASE6_BASE64_C_PARITY_SELF_TEST_CASE_COUNT=10` while covering the parity script's missing-path guards, malformed fixture-byte-token parsing, generated build template, sorted-output normalization, representative-output fail-closed drift checks, and explicit C-versus-Zig `c_output_mismatch` handling without requiring a live toolchain replay, and the committed case generator rebuilds the transient `zigux/tests/fixtures/phase6_base64_c_generated_cases.inc` include payload from `zigux/tests/fixtures/phase6_base64_vectors.zig` before the current `PHASE6_BASE64_C_PARITY_CASES=122` spot check runs.
- `zigux/tests/fixtures/phase6_checksum_vectors.zig` is the current static checksum corpus with 5 compute vectors, 2 composition vectors, 3 seeded vectors, 1 IPv4 pseudo-header vector, 3 IPv6 pseudo-header vectors, 4 carry-discipline vectors, and 6 imported KUnit random-prefix vectors.
- `zigux/tests/phase6_checksum_c_parity.zig` and `zigux/tests/fixtures/phase6_checksum_c_harness.c` now replay 27 direct C-vs-Zig checksum parity cases through `python3 scripts/zigux/check-phase6-checksum-c-parity.py`, and `python3 scripts/zigux/check-phase6-checksum-c-parity.py --self-test` now reports `PHASE6_CHECKSUM_C_PARITY_SELF_TEST_CASE_COUNT=11` while proving the committed exact 27-line expected surface, missing-path guards, and C-vs-Zig mismatch handling for the live compute, pseudo-header, carry-discipline, direct `add16` and `sub16`, and incremental replacement packet.
- `zigux/tests/fixtures/phase6_hexdump_vectors.zig` is the current static hexdump corpus with 10 parity vectors, 4 overflow vectors, 9 required-length vectors, and 4 perf replay cases, and it keeps `normalizedRowsize()`, `normalizedGroupsizeForLen()`, and `prepareExpectedLine(...)` as the shared normalization path so parity, overflow, required-length, and perf replays stay on one committed corpus table.
- `zigux/tests/phase6_hexdump_c_parity.zig` and `zigux/tests/fixtures/phase6_hexdump_c_harness.c` now replay 29 direct C-vs-Zig hexdump parity cases through `python3 scripts/zigux/check-phase6-hexdump-c-parity.py`, and `python3 scripts/zigux/check-phase6-hexdump-c-parity.py --self-test` now reports `PHASE6_HEXDUMP_C_PARITY_SELF_TEST_CASE_COUNT=8` while proving the committed exact 29-line expected surface, missing-path guards, sorted-output normalization, and C-vs-Zig mismatch handling.
- `zigux/tests/phase6_bsearch.zig` and `zigux/tests/phase6_bsearch_c_parity.zig` keep the direct lookup and external-parity corpus inline as sorted integer, descending, duplicate, singleton, empty-slice, mutable, and symbol tables, while `zigux/tests/phase6_bsearch_perf.zig` and `zigux/tests/fixtures/phase6_bsearch_vectors.zig` keep the committed perf-case table plus the fixed edge, quarter, midpoint, final-hit, and paired miss probes reviewable beside that inline helper corpus; `python3 scripts/zigux/check-phase6-bsearch-c-parity.py --self-test` currently reports `PHASE6_BSEARCH_C_PARITY_SELF_TEST_CASE_COUNT=6` so the parity script's missing-path, unexpected-extra-output, and output-normalization helpers stay reviewable without a live toolchain replay, and `python3 scripts/zigux/check-phase6-bsearch-c-parity.py` currently passes with `PHASE6_BSEARCH_C_PARITY_CASES=29`.
- No generated Phase 6 fixture artifact is committed today; current corpus determinism comes from these committed literals, normalization helpers, and sorted external parity replays.

## Review posture

- `make -C zigux phase6-validate` is the fail-fast shared catalog gate.
- `python3 scripts/zigux/check-phase6-docs-root-external-parity.py --self-test` and `python3 scripts/zigux/check-phase6-docs-root-external-parity.py` keep the docs-root external portability inventory fail-closed across `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/phase6_helper_parity_manifest.json`, and `zigux/Makefile`, so the shared Phase 6 review packet does not silently undercount that shipped checker surface.
- `python3 scripts/zigux/validate-phase6.py --self-test` currently reports `PHASE6_VALIDATOR_SELF_TEST_CASE_COUNT=43` and now fail-closes on catalog-head drift, script-README wording, catalog marker drift, perf-survey marker drift, bsearch perf comparison-budget drift, hexdump-slice perf wording drift, shared-gates drift, helper-entry drift, required-test inventory drift, and determinism-evidence drift across the shipped base64, bsearch, checksum, and hexdump packet before the broader Phase 6 review surface claims alignment.
- `make -C zigux phase6` replays the bundled Phase 6 helper tests together.
- `make -C zigux phase6-perf` replays the bundled Phase 6 perf harnesses together while keeping those microbenches out of the default helper-test lane.
- `python3 scripts/zigux/check-phase6-base64-c-parity.py --self-test` is the current tool-free reviewability check for the bounded base64 external parity script before the live `zig` plus `cc` replay runs, and it now proves the explicit `c_output_mismatch` failure contract before `python3 scripts/zigux/check-phase6-base64-c-parity.py` reruns the full `PHASE6_BASE64_C_PARITY_CASES=122` spot check.
- `python3 scripts/zigux/check-phase6-base64-catalog-evidence.py --self-test` and `python3 scripts/zigux/check-phase6-base64-catalog-evidence.py` now keep the shared base64 review packet fail-closed on the exact parked shared-packet posture, the 30 variant encode vectors, 20 variant decode vectors, `PHASE6_BASE64_C_PARITY_SELF_TEST_CASE_COUNT=10`, and `PHASE6_BASE64_C_PARITY_CASES=122` evidence recorded across this catalog, `zigux/tests/phase6_helper_parity_manifest.json`, and `scripts/zigux/check-phase6-base64-c-parity.py`.
- `python3 scripts/zigux/check-phase6-bsearch-c-parity.py --self-test` is the current tool-free reviewability check for the bounded bsearch external parity script before the live `zig` plus `cc` replay runs.
- `python3 scripts/zigux/check-phase6-checksum-c-parity.py --self-test` is the current tool-free reviewability check for the bounded checksum external parity script before the live `zig` plus `cc` replay runs, and `python3 scripts/zigux/check-phase6-checksum-c-parity.py` currently passes with `PHASE6_CHECKSUM_C_PARITY_CASES=27`.
- `python3 scripts/zigux/check-phase6-hexdump-c-parity.py --self-test` is the current tool-free reviewability check for the bounded hexdump external parity script before the live `zig` plus `cc` replay runs, and `python3 scripts/zigux/check-phase6-hexdump-c-parity.py` currently passes with `PHASE6_HEXDUMP_C_PARITY_CASES=29`.
- `Documentation/zigux/README.md` should continue to name the same four external portability review hooks through `python3 scripts/zigux/check-phase6-base64-c-parity.py`, `python3 scripts/zigux/check-phase6-bsearch-c-parity.py`, `python3 scripts/zigux/check-phase6-checksum-c-parity.py`, and `python3 scripts/zigux/check-phase6-hexdump-c-parity.py`, so the docs root does not drift back toward a validator-only reading of the bounded portability packet.
- `scripts/zigux/README.md` should continue to present those same four parity scripts as the bounded external portability spot checks inside the shared Phase 6 flow, so the scripts index does not undercount the base64 or bsearch slices.
- `zigux/tests/README.md` should continue to list the full external portability packet, including `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/phase6_base64_c_casegen.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, `zigux/tests/phase6_bsearch_c_parity.zig`, `zigux/tests/fixtures/phase6_bsearch_c_harness.c`, `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, `zigux/tests/phase6_hexdump_c_parity.zig`, and `zigux/tests/fixtures/phase6_hexdump_c_harness.c`, so the shared tests index does not regress into a checksum-plus-hexdump-only reading of the bounded portability packet.
- `zigux/tests/phase6_base64_perf.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/phase6_hexdump_perf.zig` currently carry fixture-backed relative slowdown thresholds rather than cross-machine absolute ceilings.
- the current base64 perf packet now covers the shipped standard, URL-safe, and IMAP alphabets with both padded and no-padding variant branches under the bounded slowdown gate.
- `zigux/tests/phase6_bsearch_perf.zig` currently enforces a bounded per-lookup and average comparison budget rather than a nanosecond threshold.
- the current hexdump perf packet measures helper output against the committed `fixtures.prepareExpectedLine(...)` reference path, keeping `16B-plain` at `max_slowdown_pct = 175` while the grouped ASCII replays use `max_slowdown_pct = 550` and the wider `16B-ascii-g8` replay uses `max_slowdown_pct = 600`.
- The per-helper perf targets stay reviewable only through this same bounded packet; do not treat one helper-local perf harness as closure for the whole tranche.
- Reopen this catalog only when the shipped helper inventory, test labels, fixture modules, perf entrypoints, or slice-note ownership changes.
