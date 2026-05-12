# Phase 6 Helper Parity Catalog

This catalog records the current bounded Phase 6 leaf-helper packet on `master`.

## Status
- `PHASE6_STATUS=parked`
- `PHASE6_PACKET=base64-bsearch-checksum-hexdump`
- surveyed head: `663d05b`
- shared coverage anchors: `lib/base64.c`, `lib/bsearch.c`, `lib/checksum.c`, and `lib/hexdump.c`
- exact coverage evidence: `zigux/tests/phase6_helper_parity_manifest.json` records the same parked four-helper packet through shared `roadmap_anchors` and per-helper `roadmap_anchor` fields
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
- dedicated direct C parity replay: `zigux/tests/phase6_base64_c_parity.zig`
- dedicated perf replay: `zigux/tests/phase6_base64_perf.zig`
- fixtures: `zigux/tests/fixtures/phase6_base64_vectors.zig` and `zigux/tests/fixtures/phase6_base64_c_harness.c`
- direct local C parity checker route: `python3 scripts/zigux/check-phase6-base64-c-parity.py`
- Linux-style C parity rerun route: `make -C zigux phase6-base64-c-parity`
- exact threshold marker rerun route: `python3 scripts/zigux/check-phase6-perf-threshold-markers.py`
- Linux-style perf rerun route: `make -C zigux phase6-base64-perf`
- current review posture: focused helper parity plus the dedicated 24-case direct C-vs-Zig spot check keep the shipped base64 packet reviewable without widening helper semantics, while the helper-local fixture packet now also exact-checks the public sizing, encode, decode, and invalid-input surface before the dedicated slowdown gate reruns the committed `std` and `urlsafe` baselines

### bsearch
- roadmap anchor: `lib/bsearch.c`
- helper: `lib/bsearch.zig`
- slice note: `Documentation/zigux/phase6-bsearch-slice.md`
- focused helper replay: `zigux/tests/phase6_bsearch.zig`
- focused lower- and upper-bound C ABI replay: `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`
- focused direct C ABI equality-budget replay: `zigux/tests/phase6_bsearch_c_abi_budget.zig`
- inline corpus: representative 15-element ascending and descending equality replays plus dynamic lower-, upper-, and packed-record `member_size` sweeps stay inline in `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, and `zigux/tests/phase6_bsearch_c_abi_budget.zig` instead of a separate `phase6_bsearch_vectors` fixture module
- direct local corpus evidence checker route: `python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py`
- direct local rerun route: `zig build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig`
- Linux-style rerun route: `make -C zigux phase6-bsearch-test`
- exact corpus evidence: `zigux/tests/phase6_bsearch.zig` still anchors 15-element ascending and descending equality replays with five representative hit-or-miss probes each across typed and raw lookup paths, while `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig` and `zigux/tests/phase6_bsearch_c_abi_budget.zig` still sweep dynamic lengths `0...32` plus packed-record `member_size` ranges under the same `std.math.log2_int_ceil(len) + 1` comparison budget
- current review posture: functional parity plus bounded comparison-budget evidence inside the focused replay, alongside the dedicated corpus-evidence checker, the bounds-focused C ABI companion, and the dedicated direct C ABI equality-budget replay that keep the typed and raw lower-bound, upper-bound, and equality comparator contract reviewable without widening into a separate timing-style perf target in the shipped packet today

### checksum
- roadmap anchor: `lib/checksum.c`
- helper: `lib/checksum.zig`
- slice note: `Documentation/zigux/phase6-checksum-slice.md`
- focused helper replay: `zigux/tests/phase6_checksum.zig`
- dedicated direct C parity replay: `zigux/tests/phase6_checksum_c_parity.zig`
- dedicated perf replay: `zigux/tests/phase6_checksum_perf.zig`
- fixtures: `zigux/tests/fixtures/phase6_checksum_vectors.zig` and `zigux/tests/fixtures/phase6_checksum_c_harness.c`
- direct local C parity checker route: `python3 scripts/zigux/check-phase6-checksum-c-parity.py`
- Linux-style C parity rerun route: `make -C zigux phase6-checksum-c-parity`
- exact threshold marker rerun route: `python3 scripts/zigux/check-phase6-perf-threshold-markers.py`
- Linux-style perf rerun route: `make -C zigux phase6-checksum-perf`
- current review posture: fixture-backed carry-discipline, pseudo-header, and incremental replacement parity plus the direct C-vs-Zig replay keep the shipped checksum packet reviewable without widening helper semantics, while the dedicated slowdown gate stays helper-local through the committed threshold-backed perf replay

### hexdump
- roadmap anchor: `lib/hexdump.c`
- helper: `lib/hexdump.zig`
- slice note: `Documentation/zigux/phase6-hexdump-slice.md`
- focused helper replay: `zigux/tests/phase6_hexdump.zig`
- dedicated perf replay: `zigux/tests/phase6_hexdump_perf_matrix.zig` and `zigux/tests/phase6_hexdump_perf.zig`
- fixtures: `zigux/tests/fixtures/phase6_hexdump_vectors.zig`
- direct local packet checker: `python3 scripts/zigux/check-phase6-hexdump-packet.py`
- Linux-style packet review route: `make -C zigux phase6-hexdump-review`
- direct local rerun route: `zig build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig`
- Linux-style rerun route: `make -C zigux phase6-hexdump-test`
- exact threshold marker rerun route: `python3 scripts/zigux/check-phase6-perf-threshold-markers.py`
- dedicated environment-plumbed review route: the shipped `make -C zigux phase6-hexdump-review` wrapper keeps the helper-local checker plus the focused helper replay, exact perf-matrix preflight, and ReleaseSafe perf gate on the same `PYTHON` and `ZIG` selection path instead of asking reviewers to stitch those commands together by hand
- current review posture: focused helper formatting parity plus the exact four-case perf-matrix preflight and dedicated grouped-output slowdown gate keep the shipped hexdump packet reviewable without widening helper semantics or folding the helper-local perf route into the shared `phase6` bundle today

## Shared Replay Routes
- `make -C zigux phase6-hexdump-test`
- `make -C zigux phase6-validate`
- `make -C zigux phase6`
- `make -C zigux phase6-base64-perf`
- `make -C zigux phase6-checksum-perf`
- `make -C zigux phase6-hexdump-perf`
- `make -C zigux phase6-perf`
