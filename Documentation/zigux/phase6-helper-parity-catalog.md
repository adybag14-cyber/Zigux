# Phase 6 Helper Parity Catalog

This catalog records the current bounded Phase 6 leaf-helper packet on `master`.

## Status
- `PHASE6_STATUS=parked`
- `PHASE6_PACKET=base64-bsearch-checksum-hexdump`
- surveyed head: `911470d`
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
- direct local rerun route: `zig build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig`
- Linux-style rerun route: `make -C zigux phase6-bsearch-test`
- current review posture: functional parity plus bounded comparison-budget evidence inside the focused replay, alongside the dedicated bounds-focused C ABI companion and the dedicated direct C ABI equality-budget replay that keep the typed and raw lower-bound, upper-bound, and equality comparator contract reviewable without widening into a separate timing-style perf target in the shipped packet today

### checksum
- roadmap anchor: `lib/checksum.c`
- helper expected by the shared packet: `lib/checksum.zig`
- slice note: `Documentation/zigux/phase6-checksum-slice.md`
- current missing helper-local packet: `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/phase6_checksum_perf.zig`, `zigux/tests/fixtures/phase6_checksum_vectors.zig`, and `zigux/tests/fixtures/phase6_checksum_c_harness.c`
- still-present checker and shared route references: `scripts/zigux/check-phase6-checksum-c-parity.py`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`
- direct local C parity rerun route once the helper packet is restored: `python3 scripts/zigux/check-phase6-checksum-c-parity.py`
- Linux-style C parity rerun route once the helper packet is restored: `make -C zigux phase6-checksum-c-parity`
- current review posture: blocked; the checksum roadmap anchor still belongs in the bounded Phase 6 helper packet, but current `master` no longer contains the checksum-owned Zig helper, fixture, parity, or perf replay files that used to make that row reviewable

### hexdump
- roadmap anchor: `lib/hexdump.c`
- helper: `lib/hexdump.zig`
- slice note: `Documentation/zigux/phase6-hexdump-slice.md`
- focused helper replay: `zigux/tests/phase6_hexdump.zig`
- dedicated perf replay: `zigux/tests/phase6_hexdump_perf.zig`
- fixtures: `zigux/tests/fixtures/phase6_hexdump_vectors.zig`
- direct local rerun route: `zig build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig`
- Linux-style rerun route: `make -C zigux phase6-hexdump-test`
- current review posture: focused helper formatting parity plus the dedicated grouped-output slowdown gate keep the shipped hexdump packet reviewable without widening helper semantics or folding the helper-local perf route into the shared `phase6` bundle

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
