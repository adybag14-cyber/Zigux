# Phase 3 ABI Slice

This note keeps the current `abi` review surface explicit while the shared Phase 3 packet is reconciled against current `master`.

## Current Status

- `PHASE3_ABI_MANIFEST_FILE_COUNT=shared ABI packet anchored by zigux/tests/fixtures/phase3_abi_manifest.json`
- `PHASE3_CURRENT_INTEROP_GAP=the same-lane export-shim and starter-UAPI surfaces are still present on current master, but the shared ABI reminder packet can keep stale direct phase3_abi replay entries unless the manifest-backed file inventory and packet markers drop retired phase3_abi paths together`
- `PHASE3_CURRENT_INTEROP_GAP_DETAIL=the bounded ABI lane still routes through Documentation/zigux/phase3-export-uapi-boundary-survey.md, Documentation/zigux/phase3-abi-header-family-survey.md, Documentation/zigux/phase3-linux-zigux-header-governance.md, Documentation/zigux/phase3-abi-h-boundary-next-step.md, scripts/zigux/check-phase3-abi.py, scripts/zigux/check-phase3-abi-dump-gate.py, scripts/zigux/validate-phase3-validator-support-surface.py, scripts/zigux/validate-phase3-abi-bindings-syntax.py, scripts/zigux/validate-phase3-export-uapi-survey.py, scripts/zigux/survey-phase3-abi-constant-parity.py, scripts/zigux/validate-phase3-abi-header-family-survey.py, scripts/zigux/validate-phase3-low-level-wrapper-survey.py, the manifest-backed file inventory, and the live public zigux/uapi tree, so the current requirement is to keep the surviving dump gate, starter-UAPI packet, manifest-backed file inventory, and reminder-surface markers aligned instead of leaving retired direct phase3_abi replay paths behind in only one inventory surface`
- `PHASE3_NEXT_SAFE_STEP=keep the current starter boundary bounded to zigux/uapi/version.zig plus zigux/uapi/dev_t.zig and the current low-level wrapper boundary bounded to the shipped atomic, barrier, MMIO, and narrow-unsafe survey packet; whenever a starter-UAPI companion, header-family reminder, header-governance note, direct phase3_abi replay anchor, or low-level-wrapper replay anchor changes, refresh Documentation/zigux/phase3-export-uapi-boundary-survey.md, Documentation/zigux/phase3-abi-header-family-survey.md, Documentation/zigux/phase3-linux-zigux-header-governance.md, Documentation/zigux/phase3-abi-h-boundary-next-step.md, Documentation/zigux/phase3-validator-support-surface.md, the shared ABI note, the manifest-backed file inventory, and the coupled validator surfaces together in the same packet so no reminder surface gets ahead of the tree`
- `PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig`

## Packet Markers

- `Documentation/zigux/phase3-export-uapi-boundary-survey.md`
- `Documentation/zigux/phase3-abi-header-family-survey.md`
- `Documentation/zigux/phase3-linux-zigux-header-governance.md`
- `Documentation/zigux/phase3-abi-h-boundary-next-step.md`
- `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`
- `Documentation/zigux/phase3-validator-support-surface.md`
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
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/phase3_low_level_wrappers.zig`
- `zigux/tests/fixtures/phase3_abi_manifest.json`
- `scripts/zigux/check-phase3-abi.py`
- `scripts/zigux/check-phase3-abi-dump-gate.py`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `scripts/zigux/validate-phase3-abi-bindings-syntax.py`
- `scripts/zigux/survey-phase3-abi-constant-parity.py`
- `scripts/zigux/validate-phase3-abi-header-family-survey.py`
- `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`
- `scripts/zigux/validate-phase3-validator-support-surface.py`
- `python3 scripts/zigux/check-phase3-abi.py --self-test`
- `python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test`
- `python3 scripts/zigux/run-phase3-checks.py --slug abi`
- `zig build phase3-dump --build-file zigux/tests/build.zig`
- `make -C zigux phase3-validate`
- `make -C zigux phase3`
