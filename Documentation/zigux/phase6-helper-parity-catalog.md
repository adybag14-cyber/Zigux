# Phase 6 Helper Parity Catalog

This catalog records the current bounded Phase 6 leaf-helper packet on `master`.

## Status
- `PHASE6_STATUS=partially_blocked`
- `PHASE6_PACKET=base64-bsearch-checksum-hexdump`
- surveyed head: `a0f4d7e`
- shared sequencing note: `Documentation/zigux/phase6-leaf-helper-lane-sequencing.md`
- shared perf note: `Documentation/zigux/phase6-perf-gate-survey.md`
- shared manifest: `zigux/tests/phase6_helper_parity_manifest.json`
- shared checker: `scripts/zigux/check-phase6-shared-surface.py`

## Packet Rows

### base64
- roadmap anchor: `lib/base64.c`
- helper: `lib/base64.zig`
- slice note: `Documentation/zigux/phase6-base64-slice.md`
- focused helper replay: `zigux/tests/phase6_base64.zig`
- focused slowdown-fixture companion: `zigux/tests/fixtures/phase6_base64_vectors.zig`
- still-present direct C parity scaffolding: `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`
- dedicated helper-local perf replay on current `master`: `zigux/tests/phase6_base64_perf.zig`
- direct parity packet note: the committed direct C parity scaffolding is self-contained again because `zigux/tests/phase6_base64_c_parity.zig` and `zigux/tests/phase6_base64_c_casegen.zig` now consume the compact `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig` corpus instead of the absent focused replay fixture module
- exact manifest-backed evidence: `zigux/tests/phase6_helper_parity_manifest.json` still records `24` direct C parity cases and preserves the dedicated slowdown packet as four case labels, `STD_PAD`, `STD_NO_PAD`, `URLSAFE_PAD`, and `URLSAFE_NO_PAD`, each at `iterations = 12000`, `max_encode_slowdown_pct = 150`, and `max_decode_slowdown_pct = 325`
- current review posture: reviewable; current `master` keeps the helper, the focused helper replay, the dedicated slowdown gate, the slowdown-fixture companion, and a self-contained direct C parity packet under the same bounded base64 review surface, while the broader shared Phase 6 packet stays partially blocked only by the checksum-owned gaps

### bsearch
- roadmap anchor: `lib/bsearch.c`
- helper: `lib/bsearch.zig`
- slice note: `Documentation/zigux/phase6-bsearch-slice.md`
- focused helper replay: `zigux/tests/phase6_bsearch.zig`
- focused lower- and upper-bound C ABI replay: `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`
- focused direct C ABI equality-budget replay: `zigux/tests/phase6_bsearch_c_abi_budget.zig`
- compact shared seed fixture companion: `zigux/tests/fixtures/phase6_bsearch_vectors.zig`
- direct local corpus evidence checker: `python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py`
- direct local rerun route: `zig build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig`
- Linux-style rerun route: `make -C zigux phase6-bsearch-test`
- exact manifest-backed evidence: `zigux/tests/phase6_helper_parity_manifest.json` still records a 15-element representative inline corpus, `10` typed and `10` raw lookup budget checks capped at `4` comparator calls, plus lower- and upper-bound as well as direct C ABI equality sweeps across dynamic lengths `0...32` and packed-record `member_size` ranges under the same `std.math.log2_int_ceil(len) + 1` budget
- current review posture: functional parity plus bounded comparison-budget evidence inside the focused replay, alongside the dedicated bounds-focused C ABI companion, the dedicated direct C ABI equality-budget replay, and the compact shared seed fixture companion that keep the typed and raw lower-bound, upper-bound, and equality comparator contract reviewable without widening into a separate timing-style perf target in the shipped packet today

### checksum
- roadmap anchor: `lib/checksum.c`
- helper: `lib/checksum.zig`
- slice note: `Documentation/zigux/phase6-checksum-slice.md`
- focused helper replay: `zigux/tests/phase6_checksum.zig`
- dedicated helper-local perf replay: `zigux/tests/phase6_checksum_perf.zig`
- compact shared fixture companion: `zigux/tests/fixtures/phase6_checksum_vectors.zig`
- still-present direct C parity scaffolding: `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`
- blocked route note: the helper, focused replay, perf runner, and fixture companion are present on current `master`, but `zigux/tests/phase6_build.zig` still does not add a checksum module or checksum test/perf step, so the checksum packet is not yet wired through the same direct `zig build ... --build-file zigux/tests/phase6_build.zig` route shape used by the other landed Phase 6 helpers
- make/workflow drift note: `zigux/Makefile` still names `phase6-checksum-c-parity` and `phase6-checksum-perf` as phony routes without target bodies, while `.github/workflows/zigux-bootstrap.yml` still limits checksum CI coverage to the parity checker self-test instead of running the restored checksum helper packet itself
- still-present direct C parity checker: `scripts/zigux/check-phase6-checksum-c-parity.py`
- direct local C parity rerun route: `python3 scripts/zigux/check-phase6-checksum-c-parity.py`
- exact manifest-backed evidence: `zigux/tests/phase6_helper_parity_manifest.json` still records `27` direct C parity cases and preserves the checksum slowdown packet as `64B` at `iterations = 200000` and `1501B` at `iterations = 12000`, both with `max_slowdown_pct = 150`
- current review posture: partially blocked; current `master` now keeps the checksum helper, focused replay, dedicated perf runner, fixture companion, and direct C parity scaffolding, but the routed checksum build/perf packet still lags the restored helper-owned surface so the checksum leg cannot yet claim the same runnable shared-route posture as the landed base64, bsearch, and hexdump evidence

### hexdump
- roadmap anchor: `lib/hexdump.c`
- helper: `lib/hexdump.zig`
- slice note: `Documentation/zigux/phase6-hexdump-slice.md`
- perf refresh note: `Documentation/zigux/phase6-hexdump-perf-refresh.md`
- focused helper replay: `zigux/tests/phase6_hexdump.zig`
- dedicated perf replay: `zigux/tests/phase6_hexdump_perf.zig`
- exact perf-matrix preflight: `zigux/tests/phase6_hexdump_perf_matrix.zig`
- fixtures: `zigux/tests/fixtures/phase6_hexdump_vectors.zig`
- direct local packet checker: `python3 scripts/zigux/check-phase6-hexdump-packet.py`
- direct local perf-threshold checker: `python3 scripts/zigux/check-phase6-perf-threshold-markers.py`
- Linux-style packet review route: `make -C zigux phase6-hexdump-review`
- direct local rerun route: `zig build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig`
- Linux-style rerun route: `make -C zigux phase6-hexdump-test`
- dedicated environment-plumbed review route: the shipped `make -C zigux phase6-hexdump-review` wrapper keeps the helper-local checker plus the focused helper and perf replays on the same `PYTHON` and `ZIG` selection path
- exact manifest-backed evidence: `zigux/tests/phase6_helper_parity_manifest.json` still records a four-case slowdown packet, `16B-plain-g1`, `32B-ascii-g2`, `16B-ascii-g4`, and `16B-ascii-g8`, with helper-local caps of `175`, `550`, `550`, and `600`
- current review posture: focused helper formatting parity plus the dedicated grouped-output slowdown gate keep the shipped hexdump packet reviewable without widening helper semantics or folding the helper-local perf route into the shared `phase6` bundle, while the preserved grouped-ASCII ceiling rationale stays anchored in `Documentation/zigux/phase6-hexdump-perf-refresh.md` under the same helper-owned review packet

## Shared Routes

### Reviewable on current `master`
- `python3 scripts/zigux/check-phase6-perf-threshold-markers.py`
- `make -C zigux phase6-bsearch-test`
- `make -C zigux phase6-hexdump-test`
- `make -C zigux phase6-hexdump-review`
- `make -C zigux phase6-hexdump-perf`

### Still present in shared route surfaces but currently blocked or documentary
- `make -C zigux phase6-base64-c-parity`
- `make -C zigux phase6-checksum-c-parity`
- `make -C zigux phase6-base64-perf`
- `make -C zigux phase6-checksum-perf`
- `make -C zigux phase6-perf`
- `make -C zigux phase6-validate`
- `make -C zigux phase6`
- current blocked-route posture: the slice notes above keep the focused base64 helper replay, the dedicated base64 slowdown gate, the direct base64 C parity packet, and the restored checksum helper packet readable as review surfaces, but the checksum leg remains partially blocked at the shared-route layer because `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` still lag the restored checksum helper/test/perf packet
- current perf-route posture: the shared perf survey above keeps the checksum slowdown route documentary until its helper-owned build/test wiring and wrapper bodies catch up with the restored `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig` packet, while the aggregate `phase6-perf` route should still be read as inventory evidence because the current `zigux/Makefile` readback exposes only the wrapper name instead of a committed target body
- current shared-lane posture: the broader `phase6-base64-perf`, `phase6-validate`, `phase6-perf`, and `phase6` wrappers remain part of the shared route inventory, but the documented base64 direct build step and the checksum packet's restored helper-owned files mean reviewers should cross-check the slice notes, the shared perf survey, and `zigux/tests/phase6_build.zig` before treating those wrappers as runnable packet summaries
