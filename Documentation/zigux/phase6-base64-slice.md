# Phase 6 Base64 Slice

## Status
- `PHASE6_STATUS=blocked`
- `PHASE6_SLICE=base64-leaf-helper`
- helper anchor: `lib/base64.zig`
- shared packet note: `Documentation/zigux/phase6-helper-parity-catalog.md`
- current `master` still keeps `lib/base64.zig`, `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`
- current `master` lacks `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_base64_perf.zig`, and `zigux/tests/fixtures/phase6_base64_vectors.zig`

## Review Surface
- present helper and direct C parity packet: `lib/base64.zig`, `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`
- currently missing focused helper replay and perf packet: `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_base64_perf.zig`, and `zigux/tests/fixtures/phase6_base64_vectors.zig`
- direct local C parity checker route once the missing fixture dependency is restored or the runner is decoupled from it: `python3 scripts/zigux/check-phase6-base64-c-parity.py`
- built-in parity-script self-test route: `python3 scripts/zigux/check-phase6-base64-c-parity.py --self-test`
- Linux-style C parity rerun route once the helper-local packet is restored: `make -C zigux phase6-base64-c-parity`
- current `master` cannot honestly claim the broader focused base64 replay, the helper drift guard, or the dedicated base64 slowdown gate because the committed replay and fixture files that backed those surfaces are absent from the tree
- the shipped direct C parity surface is also not currently runnable as a complete packet because `zigux/tests/phase6_base64_c_parity.zig` still imports the absent `zigux/tests/fixtures/phase6_base64_vectors.zig` fixture module
- this slice is documentary only until the missing focused replay and fixture-backed perf packet return, or the direct C parity runner is rewritten to stop depending on the absent fixture module

## Next Step
Refresh against a fresh `master` base and choose one bounded repair: either restore `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_base64_perf.zig`, and `zigux/tests/fixtures/phase6_base64_vectors.zig` so the base64 helper packet becomes runnable again, or retell the shared reminder and route surfaces so they stop advertising focused base64 replay and perf coverage that the committed tree does not contain.
