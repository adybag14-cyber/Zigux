# Phase 3 ABI Slice

This note keeps the current `abi` review surface explicit while the shared Phase 3 packet is reconciled against current `master`.

## Current Status

- `PHASE3_ABI_MANIFEST_FILE_COUNT=shared ABI packet anchored by zigux/tests/fixtures/phase3_abi_manifest.json`
- `PHASE3_CURRENT_INTEROP_GAP=the same-lane export-shim, dedicated policy-and-unsafe, starter-UAPI, and focused low-level-wrapper helper surfaces are still present on current master, but the shared ABI reminder packet can undercount the live direct phase3_abi replay files, the dedicated bindings-governance note, the dedicated ABI-and-bindings survey, the dedicated policy-and-unsafe boundary survey, the dedicated boundary-lane owner map, the dedicated include/linux/zigux.h governance validator, the dedicated low-level-wrapper build anchor, the coupled policy-and-unsafe validators, or the already-landed panic, allocator, atomic, barrier, and MMIO helpers unless the manifest-backed file inventory and packet markers stay aligned together`
- `PHASE3_CURRENT_INTEROP_GAP_DETAIL=the bounded ABI lane still routes through Documentation/zigux/phase3-bindings-governance.md, Documentation/zigux/phase3-abi-bindings-survey.md, Documentation/zigux/phase3-boundary-lane-sequencing.md, Documentation/zigux/phase3-export-uapi-boundary-survey.md, Documentation/zigux/phase3-kernel-export-shim-governance.md, Documentation/zigux/phase3-policy-unsafe-boundary-survey.md, Documentation/zigux/phase3-abi-header-family-survey.md, Documentation/zigux/phase3-linux-zigux-header-governance.md, scripts/zigux/validate-phase3-linux-zigux-header-governance.py, Documentation/zigux/phase3-abi-h-boundary-next-step.md, Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md, Documentation/zigux/phase3-validator-support-surface.md, zigux/helpers/panic_policy.zig, zigux/helpers/allocator_policy.zig, zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/unsafe/narrow.zig, scripts/zigux/check-phase3-abi.py, scripts/zigux/check-phase3-abi-dump-gate.py, scripts/zigux/validate-phase3-validator-support-surface.py, scripts/zigux/validate-phase3-abi-bindings-syntax.py, scripts/zigux/validate-phase3-export-uapi-survey.py, scripts/zigux/validate-phase3-policy-unsafe-survey.py, scripts/zigux/check-phase3-policy-byte-guards.py, scripts/zigux/check-phase3-policy-unsafe-focused-replay.py, scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py, scripts/zigux/survey-phase3-abi-constant-parity.py, scripts/zigux/validate-phase3-abi-header-family-survey.py, scripts/zigux/validate-phase3-low-level-wrapper-survey.py, the manifest-backed file inventory, zigux/tests/phase3_abi.zig, zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c, zigux/tests/fixtures/phase3_abi/expected.json, zigux/tests/phase3_low_level_wrappers.zig, zigux/tests/phase3_low_level_wrappers_build.zig, and the live public zigux/uapi tree, so the current requirement is to keep the direct phase3_abi replay plus its committed fixture pair, the dedicated bindings-governance note, the dedicated ABI-and-bindings survey, the dedicated policy-and-unsafe boundary survey, the dedicated boundary-lane owner map, the dedicated include/linux/zigux.h governance validator, the surviving dump gate, the coupled panic, allocator, atomic, barrier, MMIO, and narrow-unsafe helper packet, the coupled policy-and-unsafe validators, the focused low-level-wrapper replay and build anchor, the starter-UAPI packet, the manifest-backed file inventory, and reminder-surface markers aligned instead of leaving the direct ABI replay files, the dedicated header validator, the policy-and-unsafe survey packet, the coupled helper packet, or the low-level-wrapper replay/build anchor behind in only one inventory surface`
- `PHASE3_NEXT_SAFE_STEP=keep the current starter boundary bounded to zigux/uapi/version.zig plus zigux/uapi/dev_t.zig, keep any export-shim follow-through limited to thin status-tagged relays over those shipped starter surfaces, keep the current policy-and-unsafe boundary bounded to Documentation/zigux/phase3-policy-unsafe-boundary-survey.md plus zigux/helpers/panic_policy.zig, zigux/helpers/allocator_policy.zig, zigux/helpers/mmio.zig, zigux/unsafe/narrow.zig, scripts/zigux/validate-phase3-policy-unsafe-survey.py, scripts/zigux/check-phase3-policy-byte-guards.py, scripts/zigux/check-phase3-policy-unsafe-focused-replay.py, and scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py, keep the current low-level wrapper boundary bounded to zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/tests/phase3_low_level_wrappers.zig, and zigux/tests/phase3_low_level_wrappers_build.zig; whenever a starter-UAPI companion, bindings-governance note, ABI-and-bindings survey, policy-and-unsafe survey, boundary-lane owner map, kernel-export governance note, header-family reminder, header-governance note, dedicated include/linux/zigux.h governance validator, direct phase3_abi replay anchor, coupled panic/allocator/atomic/barrier/mmio helper, coupled policy-and-unsafe validator, or low-level-wrapper replay/build anchor changes, refresh Documentation/zigux/phase3-bindings-governance.md, Documentation/zigux/phase3-abi-bindings-survey.md, Documentation/zigux/phase3-boundary-lane-sequencing.md, Documentation/zigux/phase3-export-uapi-boundary-survey.md, Documentation/zigux/phase3-kernel-export-shim-governance.md, Documentation/zigux/phase3-policy-unsafe-boundary-survey.md, Documentation/zigux/phase3-abi-header-family-survey.md, Documentation/zigux/phase3-linux-zigux-header-governance.md, scripts/zigux/validate-phase3-linux-zigux-header-governance.py, Documentation/zigux/phase3-abi-h-boundary-next-step.md, Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md, Documentation/zigux/phase3-validator-support-surface.md, the shared ABI note, the manifest-backed file inventory, and the coupled validator surfaces together in the same packet so no reminder surface gets ahead of the tree`
- `PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig`

## Packet Markers

- `Documentation/zigux/phase3-bindings-governance.md`
- `Documentation/zigux/phase3-abi-bindings-survey.md`
- `Documentation/zigux/phase3-boundary-lane-sequencing.md`
- `Documentation/zigux/phase3-export-uapi-boundary-survey.md`
- `Documentation/zigux/phase3-kernel-export-shim-governance.md`
- `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md`
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
- `zigux/helpers/panic_policy.zig`
- `zigux/helpers/allocator_policy.zig`
- `zigux/helpers/atomic.zig`
- `zigux/helpers/barrier.zig`
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
- `scripts/zigux/check-phase3-abi.py`
- `scripts/zigux/check-phase3-abi-dump-gate.py`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `scripts/zigux/validate-phase3-policy-unsafe-survey.py`
- `scripts/zigux/check-phase3-policy-byte-guards.py`
- `scripts/zigux/check-phase3-policy-unsafe-focused-replay.py`
- `scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py`
- `scripts/zigux/validate-phase3-linux-zigux-header-governance.py`
- `scripts/zigux/validate-phase3-abi-bindings-syntax.py`
- `scripts/zigux/survey-phase3-abi-constant-parity.py`
- `scripts/zigux/validate-phase3-abi-header-family-survey.py`
- `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`
- `scripts/zigux/validate-phase3-validator-support-surface.py`
- `python3 scripts/zigux/check-phase3-abi.py --self-test`
- `python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test`
- `python3 scripts/zigux/run-phase3-checks.py --slug abi`
- `zig build phase3-dump --build-file zigux/tests/build.zig`
- `zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`
- `make -C zigux phase3-validate`
- `make -C zigux phase3`
