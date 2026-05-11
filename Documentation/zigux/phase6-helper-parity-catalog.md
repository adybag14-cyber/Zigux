# Phase 6 Helper Parity Catalog

This catalog records the current bounded Phase 6 leaf-helper packet on `master`.

## Status
- `PHASE6_STATUS=parked`
- `PHASE6_PACKET=base64-bsearch-checksum-hexdump`
- surveyed head: `277b3ab`
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
- focused direct C parity replay: `zigux/tests/phase6_base64_c_parity.zig`
- dedicated perf replay: `zigux/tests/phase6_base64_perf.zig`
- fixtures: `zigux/tests/fixtures/phase6_base64_vectors.zig` and `zigux/tests/fixtures/phase6_base64_c_harness.c`
- checker: `scripts/zigux/check-phase6-base64-c-parity.py`
- direct local C parity rerun route: `python3 scripts/zigux/check-phase6-base64-c-parity.py`
- Linux-style C parity rerun route: `make -C zigux phase6-base64-c-parity`

### bsearch
- roadmap anchor: `lib/bsearch.c`
- helper: `lib/bsearch.zig`
- slice note: `Documentation/zigux/phase6-bsearch-slice.md`
- focused helper replay: `zigux/tests/phase6_bsearch.zig`
- focused lower- and upper-bound C ABI replay: `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`
- focused direct C ABI equality-budget replay: `zigux/tests/phase6_bsearch_c_abi_budget.zig`
- fixtures: `zigux/tests/fixtures/phase6_bsearch_vectors.zig` for the bounded deterministic query-seeding and case-size corpus shared by the focused bsearch replays
- direct local rerun route: `zig build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig`
- Linux-style rerun route: `make -C zigux phase6-bsearch-test`
- exact corpus evidence: `zigux/tests/phase6_bsearch.zig` still anchors 15-element ascending and descending equality replays with five representative hit-or-miss probes each across typed and raw lookup paths, while `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig` and `zigux/tests/phase6_bsearch_c_abi_budget.zig` still sweep dynamic lengths `0...32` plus packed-record `member_size` ranges under the same `std.math.log2_int_ceil(len) + 1` comparison budget
- current review posture: functional parity plus bounded comparison-budget evidence inside the focused replay, alongside the dedicated bounds-focused C ABI companion and the dedicated direct C ABI equality-budget replay that keep the typed and raw lower-bound, upper-bound, and equality comparator contract reviewable without widening into a separate timing-style perf target in the shipped packet today

### checksum
- roadmap anchor: `lib/checksum.c`
- helper: `lib/checksum.zig`
- slice note: `Documentation/zigux/phase6-checksum-slice.md`
- focused helper replay: `zigux/tests/phase6_checksum.zig`
- focused direct C parity replay: `zigux/tests/phase6_checksum_c_parity.zig`
- dedicated perf replay: `zigux/tests/phase6_checksum_perf.zig`
- fixtures: `zigux/tests/fixtures/phase6_checksum_vectors.zig` and `zigux/tests/fixtures/phase6_checksum_c_harness.c`
- checker: `scripts/zigux/check-phase6-checksum-c-parity.py`
- exact threshold checker: `scripts/zigux/check-phase6-perf-threshold-markers.py`
- direct local C parity rerun route: `python3 scripts/zigux/check-phase6-checksum-c-parity.py`
- Linux-style C parity rerun route: `make -C zigux phase6-checksum-c-parity`
- exact threshold marker rerun route: `python3 scripts/zigux/check-phase6-perf-threshold-markers.py`

### hexdump
- roadmap anchor: `lib/hexdump.c`
- helper: `lib/hexdump.zig`
- slice note: `Documentation/zigux/phase6-hexdump-slice.md`
- focused helper replay: `zigux/tests/phase6_hexdump.zig`
- dedicated perf replay: `zigux/tests/phase6_hexdump_perf.zig`
- fixtures: `zigux/tests/fixtures/phase6_hexdump_vectors.zig`
- direct local rerun route: `zig build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig`
- Linux-style rerun route: `make -C zigux phase6-hexdump-test`
- current review posture: focused helper formatting parity plus the dedicated grouped-output slowdown gate keep the shipped hexdump packet reviewable without widening helper semantics or folding the helper-local perf route into the shared `phase6` bundle today

## Shared Routes
- `make -C zigux phase6-base64-c-parity`
- `make -C zigux phase6-bsearch-test`
- `make -C zigux phase6-checksum-c-parity`
- `make -C zigux phase6-hexdump-test`
- `make -C zigux phase6-validate`
- `make -C zigux phase6`
- `make -C zigux phase6-base64-perf`
- `make -C zigux phase6-checksum-perf`
- `make -C zigux phase6-hexdump-perf`
- `make -C zigux phase6-perf`
