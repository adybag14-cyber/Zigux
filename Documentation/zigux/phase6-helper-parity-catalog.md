# Phase 6 Helper Parity Catalog

This note records the current shared Phase 6 leaf-helper evidence bundle at the inspected `master` tip when this catalog was refreshed.

- verified head: `7bf069157b72665fcf5b05f7e0f275e9f67b00a3`

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
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

This shared catalog exists so reviewers can confirm, in one place, that the roadmap-backed Phase 6 packet still stops at the four leaf helpers and that the docs, validator, workflow, and test entrypoints all describe the same shipped surface.

## Current helper evidence

### base64

- helper: `lib/base64.zig`
- tests: `zigux/tests/phase6_base64.zig`
- perf: `zigux/tests/phase6_base64_perf.zig`
- fixtures: `zigux/tests/fixtures/phase6_base64_vectors.zig`
- slice note: `Documentation/zigux/phase6-base64-slice.md`

### bsearch

- helper: `lib/bsearch.zig`
- tests: `zigux/tests/phase6_bsearch.zig`
- perf: `zigux/tests/phase6_bsearch_perf.zig`
- external parity: `scripts/zigux/check-phase6-bsearch-c-parity.py`
- fixtures: `zigux/tests/phase6_bsearch_c_parity.zig`, `zigux/tests/fixtures/phase6_bsearch_c_harness.c`
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

The current Phase 6 perf packet is intentionally mixed. Two helpers now carry fixture-backed relative slowdown thresholds, one helper carries an algorithmic comparison-budget threshold, and one helper still stays on deterministic timing evidence without a machine-stable nanosecond ceiling.

### base64

- `zigux/tests/phase6_base64_perf.zig` replays two deterministic payloads: `64B` at `20_000` reps and `1KB` at `4_000` reps.
- the current numeric thresholds are `max_encode_slowdown_pct = 125` and `max_decode_slowdown_pct = 225` for both cases, measured against the padded `std.base64.standard` reference path.
- the harness also rechecks encode parity, decode parity, and round-trip correctness before and after the timed loops while reporting helper and reference nanoseconds per operation plus the observed slowdown percentages.

### bsearch

- `zigux/tests/phase6_bsearch_perf.zig` replays two representative sorted slices: `256` entries at `2_000` reps and `4096` entries at `500` reps.
- the machine-checked threshold is algorithmic rather than time-based: `avg_compare_calls <= std.math.log2_int_ceil(len) + 1`.
- the harness still prints `ns_per_lookup`, but no stable nanosecond ceiling is claimed today.

### checksum

- `zigux/tests/phase6_checksum_perf.zig` replays two deterministic payloads from `zigux/tests/fixtures/phase6_checksum_vectors.zig`: `64` bytes at `20_000` reps and `1501` bytes at `2_000` reps.
- the current numeric threshold is `max_slowdown_pct = 150` for both fixture cases, checked against the widened-accumulator `referencePartial` path.
- the harness also records helper and reference nanoseconds per call, helper and reference nanoseconds per byte, the observed `slowdown_pct`, and the folded checksum result.

### hexdump

- `zigux/tests/phase6_hexdump_perf.zig` replays two deterministic formatter cases: `16B-plain` at `40_000` reps and `32B-ascii-g2` at `10_000` reps.
- the current gate still requires output parity, required-length parity, and positive elapsed time while reporting `ns_per_call` and `ns_per_byte`.
- there is no hard formatter-cost threshold yet because the current lane only claims deterministic perf-sanity evidence.

## Current fixture corpus determinism

The committed Phase 6 fixture corpus is deterministic today because every shipped helper replay hangs off committed literals or sorted parity output instead of generated snapshot files.

- `zigux/tests/fixtures/phase6_base64_vectors.zig` is the current static base64 corpus with 22 standard encode vectors, 6 variant encode vectors, 22 standard decode vectors, 4 variant decode vectors, and 16 invalid decode vectors.
- `zigux/tests/fixtures/phase6_base64_c_harness.c` plus `zigux/tests/phase6_base64_c_parity.zig` replay that same representative base64 surface through `python3 scripts/zigux/check-phase6-base64-c-parity.py`, which currently passes with `PHASE6_BASE64_C_PARITY_CASES=70`.
- `zigux/tests/fixtures/phase6_checksum_vectors.zig` is the current static checksum corpus with 5 compute vectors, 2 composition vectors, 3 seeded vectors, 1 pseudo-header vector, and 4 carry-discipline vectors.
- `zigux/tests/fixtures/phase6_hexdump_vectors.zig` is the current static hexdump corpus with 7 parity vectors, 4 overflow vectors, and 7 required-length vectors, and it normalizes non-canonical formatter inputs through `normalizedRowsize()` and `normalizedGroupsizeForLen()` before expected-text generation.
- `zigux/tests/phase6_bsearch.zig` keeps the bsearch corpus inline as sorted integer and symbol tables rather than a generated fixture file, and `python3 scripts/zigux/check-phase6-bsearch-c-parity.py` currently passes with `PHASE6_BSEARCH_C_PARITY_CASES=13`.
- No generated Phase 6 fixture artifact is committed today; current corpus determinism comes from these committed literals, normalization helpers, and sorted external parity replays.

## Review posture

- `make -C zigux phase6-validate` is the fail-fast shared catalog gate.
- `make -C zigux phase6` replays the bundled Phase 6 helper tests together.
- `zigux/tests/phase6_base64_perf.zig` and `zigux/tests/phase6_checksum_perf.zig` currently carry fixture-backed relative slowdown thresholds rather than cross-machine absolute ceilings.
- `zigux/tests/phase6_bsearch_perf.zig` currently enforces a bounded comparison budget rather than a nanosecond threshold.
- `zigux/tests/phase6_hexdump_perf.zig` currently remains a deterministic formatter-cost sanity harness without a numeric slowdown ceiling.
- The per-helper perf targets stay reviewable only through this same bounded packet; do not treat one helper-local perf harness as closure for the whole tranche.
- Reopen this catalog only when the shipped helper inventory, test labels, fixture modules, perf entrypoints, or slice-note ownership changes.
