# Phase 3 ABI Slice

This note keeps the current `abi` review surface explicit while the shared Phase 3 packet is reconciled against current `master`.

## Current Status

- `PHASE3_ABI_MANIFEST_FILE_COUNT=shared ABI packet anchored by zigux/tests/fixtures/phase3_abi_manifest.json`
- `PHASE3_CURRENT_INTEROP_GAP=the direct current-master readback no longer shows a version-only starter-UAPI boundary because the shared ABI packet now ships both zigux/uapi/version.zig and zigux/uapi/dev_t.zig, but the UAPI surface still remains a bounded starter pair rather than a broader exported family`
- `PHASE3_CURRENT_INTEROP_GAP_DETAIL=zigux/uapi/version.zig now exposes boundary-header compatibility, acceptance, canonicalization, and evaluation helpers with direct tests, zigux/uapi/dev_t.zig mirrors encode and range helpers through the starter UAPI surface, and the shared ABI manifest plus its directly coupled docs-root and scripts-root reminder surfaces now name both files; the remaining same-family limit is breadth, not a missing companion file`
- `PHASE3_NEXT_SAFE_STEP=keep the current starter boundary scoped to zigux/uapi/version.zig plus zigux/uapi/dev_t.zig until a real wider UAPI packet lands; keep the shared ABI note, manifest-backed file inventory, and directly coupled reminder surfaces aligned to current master without recreating the retired dedicated export/UAPI replay family`
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
