# Phase 6 Helper Parity Catalog

This note records the current shared Phase 6 leaf-helper evidence bundle at the inspected `master` tip when this catalog was refreshed.

- verified head: `d386a77a28cfbb46abd8e7d9c5e2bdf9c93948cb`
- machine-readable inventory: `zigux/tests/phase6_helper_parity_manifest.json`

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

This shared catalog exists so reviewers can confirm, in one place, that the roadmap-backed Phase 6 packet still stops at the four leaf helpers and that the docs, validator, workflow, perf-gate survey, and test entrypoints all describe the same shipped surface. The manifest is the compact machine-readable companion for that same packet, while this note keeps the reviewer-facing perf and fixture posture explicit.

## Current helper evidence

### base64

- helper: `lib/base64.zig`
- tests: `zigux/tests/phase6_base64.zig`
- perf: `zigux/tests/phase6_base64_perf.zig`
- external parity: `scripts/zigux/check-phase6-base64-c-parity.py`
- external parity harnesses: `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/phase6_base64_c_casegen.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`
- fixtures: `zigux/tests/fixtures/phase6_base64_vectors.zig`
- slice note: `Documentation/zigux/phase6-base64-slice.md`

### bsearch

- helper: `lib/bsearch.zig`
- tests: `zigux/tests/phase6_bsearch.zig`
- shared portability coverage: `zigux/tests/phase6_bsearch.zig` now exercises both typed and raw runtime-selected comparator pointers across native and C ABI paths
- perf: `zigux/tests/phase6_bsearch_perf.zig`
- external parity: `scripts/zigux/check-phase6-bsearch-c-parity.py`
- external parity runner: `zigux/tests/phase6_bsearch_c_parity.zig`
- external parity harness: `zigux/tests/fixtures/phase6_bsearch_c_harness.c`
- slice note: `Documentation/zigux/phase6-bsearch-slice.md`

### checksum

- helper: `lib/checksum.zig`
- tests: `zigux/tests/phase6_checksum.zig`
- perf: `zigux/tests/phase6_checksum_perf.zig`
- fixtures: `zigux/tests/fixtures/phase6_checksum_vectors.zig`
- slice note: `Documentation/zigux/phase6-checksum-slice.md`

### hexdump

- helper: `lib/hexdump.zig`
- tests: `zigux/tests/phase6_hexdump.zig`
- perf: `zigux/tests/phase6_hexdump_perf.zig`
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

- `zigux/tests/fixtures/phase6_base64_vectors.zig` is the current static base64 corpus with 22 standard encode vectors, 18 variant encode vectors, 22 standard decode vectors, 12 variant decode vectors, and 22 invalid decode vectors.
- `zigux/tests/fixtures/phase6_base64_c_harness.c`, `zigux/tests/phase6_base64_c_casegen.zig`, and `zigux/tests/phase6_base64_c_parity.zig` replay that same representative base64 surface through `python3 scripts/zigux/check-phase6-base64-c-parity.py`; `python3 scripts/zigux/check-phase6-base64-c-parity.py --self-test` currently reports `PHASE6_BASE64_C_PARITY_SELF_TEST_CASE_COUNT=7`, keeping the parity script's missing-path guards, generated build template, and sorted-output normalization reviewable without a live toolchain replay, and the committed case generator still rebuilds the C include payload from `zigux/tests/fixtures/phase6_base64_vectors.zig` before the current `PHASE6_BASE64_C_PARITY_CASES=96` spot check runs.
- `zigux/tests/fixtures/phase6_checksum_vectors.zig` is the current static checksum corpus with 5 compute vectors, 2 composition vectors, 3 seeded vectors, 1 IPv4 pseudo-header vector, 2 IPv6 pseudo-header vectors, 4 carry-discipline vectors, and 6 imported KUnit random-prefix vectors.
- `zigux/tests/fixtures/phase6_hexdump_vectors.zig` is the current static hexdump corpus with 9 parity vectors, 4 overflow vectors, 9 required-length vectors, and 4 perf replay cases, and it keeps `normalizedRowsize()`, `normalizedGroupsizeForLen()`, and `prepareExpectedLine(...)` as the shared normalization path so parity, overflow, required-length, and perf replays stay on one committed corpus table.
- `zigux/tests/phase6_bsearch.zig` and `zigux/tests/phase6_bsearch_c_parity.zig` keep the current bsearch corpus inline as sorted integer, descending, duplicate, singleton, empty-slice, mutable, and symbol tables rather than a generated fixture file, `python3 scripts/zigux/check-phase6-bsearch-c-parity.py --self-test` currently reports `PHASE6_BSEARCH_C_PARITY_SELF_TEST_CASE_COUNT=6` so the parity script's missing-path, unexpected-extra-output, and output-normalization helpers stay reviewable without a live toolchain replay, and `python3 scripts/zigux/check-phase6-bsearch-c-parity.py` currently passes with `PHASE6_BSEARCH_C_PARITY_CASES=29`.
- No generated Phase 6 fixture artifact is committed today; current corpus determinism comes from these committed literals, normalization helpers, and sorted external parity replays.

## Review posture

- `make -C zigux phase6-validate` is the fail-fast shared catalog gate.
- `python3 scripts/zigux/validate-phase6.py --self-test` currently reports `PHASE6_VALIDATOR_SELF_TEST_CASE_COUNT=13` and now fail-closes on catalog-head drift, script-README drift, catalog marker drift, perf-survey marker drift, shared-gates drift, and determinism-evidence drift across the shipped base64, bsearch, checksum, and hexdump packet before the broader Phase 6 review surface claims alignment.
- `make -C zigux phase6` replays the bundled Phase 6 helper tests together.
- `python3 scripts/zigux/check-phase6-base64-c-parity.py --self-test` is the current tool-free reviewability check for the bounded base64 external parity script before the live `zig` plus `cc` replay runs.
- `python3 scripts/zigux/check-phase6-bsearch-c-parity.py --self-test` is the current tool-free reviewability check for the bounded bsearch external parity script before the live `zig` plus `cc` replay runs.
- `zigux/tests/phase6_base64_perf.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/phase6_hexdump_perf.zig` currently carry fixture-backed relative slowdown thresholds rather than cross-machine absolute ceilings.
- the current base64 perf packet now covers the shipped standard, URL-safe, and IMAP alphabets with both padded and no-padding variant branches under the bounded slowdown gate.
- `zigux/tests/phase6_bsearch_perf.zig` currently enforces a bounded per-lookup and average comparison budget rather than a nanosecond threshold.
- the current hexdump perf packet measures helper output against the committed `fixtures.prepareExpectedLine(...)` reference path, keeping `16B-plain` at `max_slowdown_pct = 175` while the grouped ASCII replays use `max_slowdown_pct = 550` and the wider `16B-ascii-g8` replay uses `max_slowdown_pct = 600`.
- The per-helper perf targets stay reviewable only through this same bounded packet; do not treat one helper-local perf harness as closure for the whole tranche.
- Reopen this catalog only when the shipped helper inventory, test labels, fixture modules, perf entrypoints, or slice-note ownership changes.
