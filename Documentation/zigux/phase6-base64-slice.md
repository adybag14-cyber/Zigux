# Phase 6 Base64 Slice

## Status
- `PHASE6_STATUS=blocked`
- `PHASE6_SLICE=base64-leaf-helper`
- helper anchor: `lib/base64.zig`
- shared packet note: `Documentation/zigux/phase6-helper-parity-catalog.md`
- current `master` still keeps `lib/base64.zig`, `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`
- current `master` lacks `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_base64_perf.zig`, and `zigux/tests/fixtures/phase6_base64_vectors.zig`

## Review Surface
- present helper and direct C parity packet: `lib/base64.zig`, `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`
- currently missing focused helper replay and perf packet: `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_base64_perf.zig`, and `zigux/tests/fixtures/phase6_base64_vectors.zig`
- direct local C parity checker route: `python3 scripts/zigux/check-phase6-base64-c-parity.py`
- built-in parity-script self-test route: `python3 scripts/zigux/check-phase6-base64-c-parity.py --self-test`
- shared route inventory still names `make -C zigux phase6-base64-c-parity`, but this lane only re-established the direct local parity packet and did not retell the broader shared-route surfaces
- current `master` cannot honestly claim the broader focused base64 replay, the helper drift guard, or the dedicated base64 slowdown gate because the committed replay and fixture files that backed those surfaces are absent from the tree
- the shipped direct C parity surface is now self-contained again because `zigux/tests/phase6_base64_c_parity.zig` and `zigux/tests/phase6_base64_c_casegen.zig` both read the compact committed `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig` corpus instead of the absent focused replay fixture module
- this slice remains partially landed until the missing focused replay and fixture-backed perf packet return, but the direct local C parity runner is again a truthful review surface on current `master`

## Next Step
Refresh against a fresh `master` base and choose one bounded repair: either restore `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_base64_perf.zig`, and `zigux/tests/fixtures/phase6_base64_vectors.zig` so the broader base64 helper packet becomes runnable again, or keep the self-contained direct C parity corpus synchronized without widening into the shared Phase 6 route inventory.
