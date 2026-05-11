# Phase 3 ABI Slice

This note keeps the current `abi` review surface explicit while the shared Phase 3 packet is reconciled against current `master`.

## Current Status

- `PHASE3_ABI_MANIFEST_FILE_COUNT=shared ABI packet anchored by zigux/tests/fixtures/phase3_abi_manifest.json`
- `PHASE3_CURRENT_INTEROP_GAP=no same-lane export-shim or starter-UAPI validator gap is currently visible on the direct current-master readback: the shared validator, manifest-backed file inventory, and live public zigux/uapi tree now all keep zigux/uapi/dev_t.zig explicit beside zigux/uapi/version.zig`
- `PHASE3_CURRENT_INTEROP_GAP_DETAIL=the bounded ABI lane still routes through scripts/zigux/check-phase3-abi.py, scripts/zigux/check-phase3-abi-dump-gate.py, scripts/zigux/validate-phase3-abi-bindings-syntax.py, scripts/zigux/survey-phase3-abi-constant-parity.py, and scripts/zigux/validate-phase3-abi-header-family-survey.py, so the current requirement is to keep any future starter-UAPI growth paired with shared-validator, manifest, and reminder-surface refreshes instead of letting one review surface outrun the others`
- `PHASE3_NEXT_SAFE_STEP=keep the current starter boundary bounded to zigux/uapi/version.zig plus zigux/uapi/dev_t.zig; if a fresh top-level starter-UAPI companion lands, update the shared ABI note, manifest-backed file inventory, and directly coupled reminder surfaces together in the same packet so no review surface gets ahead of the tree`
- `PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig`

## Packet Markers

- `include/linux/zigux.h`
- `include/zigux/abi.h`
- `include/zigux/dev_t.h`
- `zigux/bindings/abi.zig`
- `zigux/bindings/dev_t.zig`
- `zigux/bindings/notifier_abi.zig`
- `zigux/helpers/layout_assert.zig`
- `zigux/kernel/export_shim.zig`
- `zigux/unsafe/narrow.zig`
- `zigux/uapi/version.zig`
- `zigux/uapi/dev_t.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c`
- `zigux/tests/fixtures/phase3_abi/expected.json`
- `zigux/tests/fixtures/phase3_abi_manifest.json`
- `scripts/zigux/check-phase3-abi-dump-gate.py`
- `python3 scripts/zigux/check-phase3-abi-dump-gate.py --self-test`
- `python3 scripts/zigux/check-phase3-abi-dump-gate.py`
- `scripts/zigux/validate-phase3-abi-bindings-syntax.py`
- `scripts/zigux/survey-phase3-abi-constant-parity.py`
- `scripts/zigux/validate-phase3-abi-header-family-survey.py`
- `python3 scripts/zigux/run-phase3-checks.py --slug abi`
- `zig build phase3-dump --build-file zigux/tests/build.zig`
- `make -C zigux phase3-validate`
- `make -C zigux phase3`
