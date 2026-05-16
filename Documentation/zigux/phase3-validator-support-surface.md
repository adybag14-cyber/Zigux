# Phase 3 Validator Support Surface

This note records the validator-facing ABI support vocabulary that Phase 3 still routes through on current `master`, including reminder-only or currently missing companion surfaces that the existing Phase 3 checks still name explicitly.

## Current packet
scripts/zigux/check-phase3-abi.py
scripts/zigux/validate-phase3-export-uapi-survey.py
scripts/zigux/validate-phase3-linux-zigux-header-governance.py
scripts/zigux/validate-phase3-abi-header-family-survey.py
scripts/zigux/validate-phase3-validator-support-surface.py
include/zigux/dev_t.h
zigux/uapi/version.zig
zigux/uapi/dev_t.zig
zigux/bindings/abi.zig
zigux/bindings/dev_t.zig
zigux/bindings/notifier_abi.zig
zigux/tests/phase3_export_uapi_layout.zig
zigux/tests/phase3_export_uapi_layout_build.zig
zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig
make -C zigux phase3-export-uapi-layout-test
zigux/tests/phase3_low_level_wrappers.zig
zigux/tests/phase3_low_level_wrappers_build.zig
zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig
make -C zigux phase3-low-level-wrappers-test
Documentation/zigux/phase3-kernel-export-shim-governance.md
Documentation/zigux/phase3-abi-bindings-survey.md
Documentation/zigux/phase3-bindings-governance.md
Documentation/zigux/phase3-export-uapi-boundary-survey.md
Documentation/zigux/phase3-abi-header-family-survey.md
Documentation/zigux/phase3-abi-h-boundary-next-step.md
scripts/zigux/validate-phase3-validator-support-surface.py
shipped helper entrypoints on current `master`

## Review boundary
This review boundary stays narrow: it records the validator-support packet and current gaps without widening into new Phase 3 helper families or deep-core freeze-map work.

## Shared reminder
scripts/zigux/README.md
zigux/tests/README.md
scripts/zigux/validate_phase3_selftest.py
scripts/zigux/validate-phase3-validator-support-surface.py
Documentation/zigux/phase3-abi-bindings-survey.md
Documentation/zigux/phase3-bindings-governance.md
Documentation/zigux/phase3-abi-header-family-survey.md
Documentation/zigux/phase3-abi-h-boundary-next-step.md
Documentation/zigux/review-checklist.md
scripts/zigux/validate-phase3-export-uapi-survey.py
scripts/zigux/validate-phase3-linux-zigux-header-governance.py
Documentation/zigux/phase3-kernel-export-shim-governance.md
Documentation/zigux/phase3-policy-unsafe-boundary-survey.md
Documentation/zigux/phase3-export-uapi-boundary-survey.md
include/zigux/dev_t.h
zigux/uapi/version.zig
zigux/uapi/dev_t.zig
zigux/bindings/abi.zig
zigux/bindings/dev_t.zig
zigux/bindings/notifier_abi.zig
zigux/tests/phase3_export_uapi_layout.zig
zigux/tests/phase3_export_uapi_layout_build.zig
zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig
make -C zigux phase3-export-uapi-layout-test
zigux/kernel/export_shim.zig
keep the canonical `include/zigux/dev_t.h` plus `zigux/uapi/version.zig`
starter-companion split explicit here whenever this validator-support packet
names the dedicated header-family survey and next-step note
naming that validator directly
kernel-facing governance note is already a broad
keep `zigux/bindings/dev_t.zig` explicit beside `zigux/bindings/abi.zig`
current broad `scripts/zigux/README.md` and `zigux/tests/README.md` reminders still route header-governance context through the paired survey and next-step notes instead of naming `scripts/zigux/validate-phase3-linux-zigux-header-governance.py` directly
zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig
zigux/tests/phase3_low_level_wrappers.zig
zigux/tests/phase3_low_level_wrappers_build.zig
scripts/zigux/check-phase3-abi.py
keep `scripts/zigux/check-phase3-abi.py` explicit in this note even though broad summaries still route that focused ABI gate through shared entrypoints
scripts/zigux/validate-phase3.py
scripts/zigux/check-phase3-selftest-surface.py
scripts/zigux/check-phase3-readme-tooling-inventory.py
scripts/zigux/check-phase3-catalog-selftest.py
scripts/zigux/check-phase3-abi-dump-gate.py
scripts/zigux/validate-phase3-policy-unsafe-survey.py
scripts/zigux/check-phase3-policy-byte-guards.py
scripts/zigux/check-phase3-policy-unsafe-focused-replay.py
scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py
scripts/zigux/validate-phase3-low-level-wrapper-survey.py
scripts/zigux/validate-phase3-abi-header-family-survey.py
scripts/zigux/validate-phase3-abi-bindings-syntax.py
scripts/zigux/survey-phase3-abi-constant-parity.py
scripts/zigux/phase3_catalog.py
scripts/zigux/phase3_check_lib.py
scripts/zigux/generate-phase3-check-wrappers.py
scripts/zigux/run-phase3-checks.py
python3 scripts/zigux/phase3_catalog.py --audit-doc-sync
python3 scripts/zigux/run-phase3-checks.py --slug abi
make -C zigux phase3-validate
make -C zigux phase3-selftest
make -C zigux phase3