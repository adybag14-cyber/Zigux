# Phase 3 ABI Slice

This note keeps the current `abi` review surface explicit while the shared Phase 3 packet is reconciled against current `master`.

## Current Status

- `PHASE3_ABI_MANIFEST_FILE_COUNT=shared ABI packet anchored by zigux/tests/fixtures/phase3_abi_manifest.json`
- `PHASE3_CURRENT_INTEROP_GAP=the direct current-master readback still shows ABI packet drift because Documentation/zigux/phase3-abi-slice.md was missing and direct GitHub contents reads now 404 for zigux/bindings/abi.zig and zigux/tests/phase3_abi.zig even while the shipped validator packet still points at them`
- `PHASE3_CURRENT_INTEROP_GAP_DETAIL=the bounded ABI lane still routes through scripts/zigux/check-phase3-abi.py, scripts/zigux/check-phase3-abi-dump-gate.py, scripts/zigux/validate-phase3-abi-bindings-syntax.py, scripts/zigux/survey-phase3-abi-constant-parity.py, and scripts/zigux/validate-phase3-abi-header-family-survey.py, so the missing docs-root ABI slice note is a real review-surface regression before python3 scripts/zigux/run-phase3-checks.py --slug abi can be trusted again`
- `PHASE3_NEXT_SAFE_STEP=reconcile the live ABI packet inventory around zigux/bindings/abi.zig, zigux/tests/phase3_abi.zig, zigux/tests/phase3_abi_dump.zig, zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c, zigux/tests/fixtures/phase3_abi/expected.json, and zigux/tests/fixtures/phase3_abi_manifest.json, then rerun python3 scripts/zigux/run-phase3-checks.py --slug abi, zig build phase3-dump --build-file zigux/tests/build.zig, make -C zigux phase3-validate, and make -C zigux phase3`
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
