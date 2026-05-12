# Phase 3 ABI Slice

This note keeps the current `abi` review surface explicit while the shared Phase 3 packet is reconciled against current `master`.

## Current Status

- `PHASE3_ABI_MANIFEST_FILE_COUNT=shared ABI packet anchored by zigux/tests/fixtures/phase3_abi_manifest.json`
- `PHASE3_CURRENT_INTEROP_GAP=the shared ABI reminder packet still has kernel-export-shim, export/UAPI, header-family, and policy-and-unsafe anchoring gap: current master ships dedicated kernel export-shim governance, export/UAPI survey, header-family survey, header-governance, policy-and-unsafe survey, and bounded next-step notes, but the broader ABI slice can still overstate a no-gap state unless those companion surfaces stay named and refreshed together`
- `PHASE3_CURRENT_INTEROP_GAP_DETAIL=the bounded ABI lane still routes through Documentation/zigux/phase3-kernel-export-shim-governance.md, Documentation/zigux/phase3-export-uapi-boundary-survey.md, Documentation/zigux/phase3-abi-header-family-survey.md, Documentation/zigux/phase3-linux-zigux-header-governance.md, Documentation/zigux/phase3-policy-unsafe-boundary-survey.md, Documentation/zigux/phase3-abi-h-boundary-next-step.md, scripts/zigux/check-phase3-abi.py, scripts/zigux/check-phase3-abi-dump-gate.py, scripts/zigux/check-phase3-policy-byte-guards.py, scripts/zigux/check-phase3-policy-unsafe-focused-replay.py, scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py, scripts/zigux/validate-phase3-policy-unsafe-survey.py, scripts/zigux/validate-phase3-validator-support-surface.py, scripts/zigux/validate-phase3-abi-bindings-syntax.py, scripts/zigux/validate-phase3-export-uapi-survey.py, scripts/zigux/survey-phase3-abi-constant-parity.py, scripts/zigux/validate-phase3-abi-header-family-survey.py, scripts/zigux/validate-phase3-low-level-wrapper-survey.py, the manifest-backed file inventory, and the live public zigux/uapi tree, so the current requirement is to keep the dedicated kernel export-shim governance note, export/UAPI survey, header-family survey, header-governance note, policy-and-unsafe survey, bounded next-step note, validator-support note, shared ABI reminder packet, and the coupled policy-and-unsafe checker surfaces refreshed together instead of letting the broad slice outrun the starter boundary or shared policy packet`
- `PHASE3_NEXT_SAFE_STEP=keep the current starter boundary bounded to zigux/kernel/export_shim.zig, zigux/uapi/version.zig, and zigux/uapi/dev_t.zig, keep the current low-level wrapper boundary bounded to the shipped atomic, barrier, MMIO, and narrow-unsafe survey packet, and keep the current policy-and-unsafe boundary bounded to the shipped explicit panic, allocator, MMIO-policy, and narrow-unsafe packet; whenever a starter kernel relay, starter-UAPI companion, header-family reminder, header-governance note, policy-and-unsafe survey anchor, panic-policy helper, allocator-policy helper, MMIO policy guard, or low-level-wrapper replay anchor changes, refresh Documentation/zigux/phase3-kernel-export-shim-governance.md, Documentation/zigux/phase3-export-uapi-boundary-survey.md, Documentation/zigux/phase3-abi-header-family-survey.md, Documentation/zigux/phase3-linux-zigux-header-governance.md, Documentation/zigux/phase3-policy-unsafe-boundary-survey.md, Documentation/zigux/phase3-abi-h-boundary-next-step.md, Documentation/zigux/phase3-validator-support-surface.md, the shared ABI note, the manifest-backed file inventory, and the coupled validator surfaces together in the same packet so no reminder surface gets ahead of the tree`
- `PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig`

## Packet Markers

- `Documentation/zigux/phase3-kernel-export-shim-governance.md`
- `Documentation/zigux/phase3-export-uapi-boundary-survey.md`
- `Documentation/zigux/phase3-abi-header-family-survey.md`
- `Documentation/zigux/phase3-linux-zigux-header-governance.md`
- `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md`
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
- `zigux/helpers/panic_policy.zig`
- `zigux/helpers/allocator_policy.zig`
- `zigux/helpers/mmio.zig`
- `zigux/kernel/export_shim.zig`
- `zigux/unsafe/narrow.zig`
- `zigux/uapi/version.zig`
- `zigux/uapi/dev_t.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/phase3_low_level_wrappers.zig`
- `zigux/tests/phase3_low_level_wrappers_build.zig`
- `zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c`
- `zigux/tests/fixtures/phase3_abi/expected.json`
- `zigux/tests/fixtures/phase3_abi_manifest.json`
- `scripts/zigux/check-phase3-abi-dump-gate.py`
- `scripts/zigux/check-phase3-policy-byte-guards.py`
- `scripts/zigux/check-phase3-policy-unsafe-focused-replay.py`
- `scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py`
- `scripts/zigux/validate-phase3-policy-unsafe-survey.py`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `scripts/zigux/validate-phase3-abi-bindings-syntax.py`
- `scripts/zigux/survey-phase3-abi-constant-parity.py`
- `scripts/zigux/validate-phase3-abi-header-family-survey.py`
- `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`
- `scripts/zigux/validate-phase3-validator-support-surface.py`
- `python3 scripts/zigux/check-phase3-policy-byte-guards.py`
- `python3 scripts/zigux/check-phase3-policy-unsafe-focused-replay.py`
- `python3 scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py`
- `python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py`
- `python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test`
- `python3 scripts/zigux/run-phase3-checks.py --slug abi`
- `zig build phase3-dump --build-file zigux/tests/build.zig`
- `make -C zigux phase3-validate`
- `make -C zigux phase3`
