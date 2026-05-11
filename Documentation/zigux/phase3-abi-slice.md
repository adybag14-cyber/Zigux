# Phase 3 ABI Slice

This note keeps the current `abi` review surface explicit while the shared Phase 3 packet is reconciled against current `master`.

## Current Status

- `PHASE3_ABI_MANIFEST_FILE_COUNT=shared ABI packet anchored by zigux/tests/fixtures/phase3_abi_manifest.json`
- `PHASE3_CURRENT_INTEROP_GAP=the direct current-master readback still shows one bounded starter-UAPI reminder drift because this shared ABI note still says zigux/uapi/dev_t.zig ships even though the shared validator and live public zigux/uapi tree keep the starter surface version-only on current master`
- `PHASE3_CURRENT_INTEROP_GAP_DETAIL=zigux/uapi/version.zig still carries the current starter UAPI boundary, and the bounded ABI lane still routes through scripts/zigux/check-phase3-abi.py, scripts/zigux/check-phase3-abi-dump-gate.py, scripts/zigux/validate-phase3-abi-bindings-syntax.py, scripts/zigux/survey-phase3-abi-constant-parity.py, and scripts/zigux/validate-phase3-abi-header-family-survey.py, so this shared note has to stay truthful before python3 scripts/zigux/run-phase3-checks.py --slug abi can be trusted as a current-master replay reminder`
- `PHASE3_NEXT_SAFE_STEP=keep the current starter boundary version-only until a real zigux/uapi/dev_t.zig packet lands; when that bounded UAPI companion becomes real, update the shared ABI note, manifest-backed file inventory, and directly coupled reminder surfaces together in the same packet so no review surface gets ahead of the tree`
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
