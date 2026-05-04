# Phase 6 Perf Gate Survey

This note records the current Phase 6 helper-microbench packet against the roadmap's `perf gates for math-sensitive helpers` requirement.

## Scope

The current bounded Phase 6 perf packet still stops at the four roadmap-backed leaf helpers:

- `lib/base64.zig`
- `lib/bsearch.zig`
- `lib/checksum.zig`
- `lib/hexdump.zig`

The shared entrypoints for that packet remain:

- `python3 scripts/zigux/validate-phase6.py`
- `make -C zigux phase6-validate`
- `make -C zigux phase6`
- `make -C zigux phase6-perf`
- `make -C zigux phase6-base64-perf`
- `make -C zigux phase6-bsearch-perf`
- `make -C zigux phase6-checksum-perf`
- `make -C zigux phase6-hexdump-perf`

The shared packet posture is also parked after the current helper-local parity and perf surface cleared the bounded Phase 6 goal.

The new aggregate `make -C zigux phase6-perf` path exists so the already-shipped helper-local perf gates can be replayed together without widening the packet into cross-machine absolute thresholds or folding those heavier microbenches into the default `make -C zigux phase6` helper-test lane.

## Current measurement posture

### base64

- `zigux/tests/phase6_base64_perf.zig` replays ten deterministic cases across the shipped standard, URL-safe, and IMAP alphabets using the two committed `64B` and `1KB` payload cases from `zigux/tests/fixtures/phase6_base64_vectors.zig`.
- the current gate is a fixture-backed relative slowdown check, not an absolute nanosecond ceiling: `max_encode_slowdown_pct = 190` and `max_decode_slowdown_pct = 320`.
- the harness reports helper and reference nanoseconds per operation, but review should treat the machine-checked ceiling as the slowdown percentage rather than the printed wall-clock number.

### bsearch

- `zigux/tests/phase6_bsearch_perf.zig` replays deterministic hit and miss queries across `256`, `4096`, and `65536` entry slices using the committed case table from `zigux/tests/fixtures/phase6_bsearch_vectors.zig`.
- the current gate is structural rather than time-based: each lookup and the average lookup path must stay within `std.math.log2_int_ceil(len) + 1` comparator calls.
- the harness still prints `ns_per_lookup`, but that value is review evidence only and is not currently a shipped threshold.

### checksum

- `zigux/tests/phase6_checksum_perf.zig` replays the deterministic `64` byte and `1501` byte payloads from `zigux/tests/fixtures/phase6_checksum_vectors.zig`.
- the current gate is a fixture-backed relative slowdown check against the widened-accumulator `referencePartial` path: `max_slowdown_pct = 150` for both replay cases.
- the harness also reports helper and reference nanoseconds per call and per byte, but the enforced contract remains the slowdown percentage rather than the raw timing output.

### hexdump

- `zigux/tests/phase6_hexdump_perf.zig` replays the deterministic `16B-plain`, `32B-ascii-g2`, `16B-ascii-g4`, and `16B-ascii-g8` formatter cases from `zigux/tests/fixtures/phase6_hexdump_vectors.zig`.
- the current gate is a fixture-backed relative slowdown check against `fixtures.prepareExpectedLine(...)`: `max_slowdown_pct = 175` for `16B-plain`, `max_slowdown_pct = 550` for the grouped ASCII `32B-ascii-g2` and `16B-ascii-g4` replays, and `max_slowdown_pct = 600` for the wider native-endian `16B-ascii-g8` replay.
- the harness also reports helper and reference nanoseconds per call and per byte plus the required formatted-line length, but the enforced contract remains the slowdown percentage.

## Gap Versus Roadmap Wording

The roadmap asks for `perf gates for math-sensitive helpers`. Current `master` now satisfies that requirement only in a bounded helper-local sense:

- every shipped helper has an explicit perf review path
- the shared `make -C zigux phase6-perf` replay now runs those helper-local gates together through one bounded aggregate entrypoint
- three helpers use fixture-backed relative slowdown ceilings
- one helper uses an algorithmic comparison budget instead of a timing ceiling
- no helper currently claims a stable cross-machine nanosecond threshold

That means the live Phase 6 packet should be read as a reviewable microbench-and-guardrail bundle, not as a claim of portable absolute performance closure.

## Review Guardrails

- refresh this note when a Phase 6 helper gains or loses a threshold, changes the perf corpus, or changes the current comparison-budget contract
- refresh this note and `zigux/tests/phase6_helper_parity_manifest.json` together when the shared `make -C zigux phase6-perf` replay path changes
- refresh `Documentation/zigux/review-checklist.md` in the same change when the shared Phase 6 validator path, docs-root external-parity guard, or helper-local perf posture changes so the top-level review packet keeps naming the same Phase 6 evidence bundle
- `python3 scripts/zigux/validate-phase6.py --self-test` now also checks that `Documentation/zigux/phase6-hexdump-slice.md` keeps the grouped-ASCII slowdown wording aligned with the shipped `zigux/tests/phase6_hexdump_perf.zig` and `zigux/tests/fixtures/phase6_hexdump_vectors.zig` packet, so hexdump threshold drift fails before broader Phase 6 replay claims stay green
- `python3 scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py --self-test` and `python3 scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py` now keep the shipped checksum and hexdump perf-marker packet fail-closed around the per-call, per-byte, slowdown, folded-checksum, required-length, and reference-path reporting markers before broader Phase 6 replay claims stay green
- refresh `Documentation/zigux/phase6-helper-parity-catalog.md` in the same change when the shared packet posture changes
- do not treat a helper-local perf improvement as justification to widen Phase 6 beyond the current four-helper packet
- do not translate the printed nanosecond output into a product-wide performance promise without a dedicated cross-machine threshold lane
