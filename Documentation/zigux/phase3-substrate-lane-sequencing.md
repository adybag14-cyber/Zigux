# Phase 3 Substrate Lane Sequencing

This note turns the current Phase 3 substrate evidence on `master` into one bounded owner map so nearby runs do not overlap the same packet from different directions.

It is a sequencing note, not approval for new substrate growth.

## Current Owner Map

Keep the shared Phase 3 substrate split on purpose.

- shared ABI summary and validator-support packet: `Documentation/zigux/phase3-abi-slice.md`, `scripts/zigux/validate-phase3.py`, `scripts/zigux/check-phase3-catalog-selftest.py`, `scripts/zigux/check-phase3-readme-tooling-inventory.py`, `scripts/zigux/check-phase3-abi-dump-gate.py`, `scripts/zigux/check-phase3-selftest-surface.py`, and `zigux/tests/fixtures/phase3_abi_manifest.json`
- ABI header and curated bindings parity packet: `include/zigux/abi.h`, `zigux/bindings/abi.zig`, `zigux/tests/phase3_abi_dump.zig`, `zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c`, `zigux/tests/fixtures/phase3_abi/expected.json`, `scripts/zigux/check-phase3-abi.py`, `scripts/zigux/validate-phase3-abi-bindings-syntax.py`, and `scripts/zigux/survey-phase3-abi-constant-parity.py`
- policy and unsafe packet: `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md`, `scripts/zigux/validate-phase3-policy-unsafe-survey.py`, `scripts/zigux/check-phase3-policy-byte-guards.py`, and `zigux/unsafe/narrow.zig`
- low-level wrapper packet: `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `zigux/helpers/allocator_policy.zig`, `zigux/helpers/panic_policy.zig`, `zigux/helpers/atomic.zig`, `zigux/helpers/barrier.zig`, `zigux/helpers/mmio.zig`, and `zigux/tests/phase3_low_level_wrappers.zig`
- export shim and starter UAPI packet: `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `scripts/zigux/validate-phase3-export-uapi-survey.py`, `zigux/kernel/export_shim.zig`, `zigux/uapi/version.zig`, `include/linux/zigux.h`, and `zigux/tests/phase3_export_uapi_layout.zig`

## Anti-Overlap Rules

Keep the next follow-up inside the smallest packet that actually moved.

- shared-summary or manifest-count repairs should update only the shared ABI slice note, validator-support surface, or shared inventory wording unless a packet-local file moved too
- ABI header or bindings parity work should stay inside `include/zigux/abi.h`, `zigux/bindings/abi.zig`, the shared dump replay, and the matching fixture packet rather than widening into export/UAPI or unsafe-note wording
- policy and unsafe follow-up should stay inside the dedicated unsafe survey, `zigux/unsafe/narrow.zig`, and the packet-local byte-guard or focused replay wiring rather than rewriting ABI parity or export/UAPI layout claims
- low-level wrapper follow-up should stay inside the wrapper survey, the wrapper helpers, and `zigux/tests/phase3_low_level_wrappers.zig` rather than rewriting shared manifest counts or starter UAPI ownership
- export/UAPI follow-up should stay inside the dedicated export/UAPI survey, `zigux/tests/phase3_export_uapi_layout.zig`, `zigux/kernel/export_shim.zig`, `zigux/uapi/version.zig`, and `include/linux/zigux.h` rather than claiming the broader ABI constant-parity packet or the dedicated unsafe packet

## Next Shared-Summary Rule

If a future shared Phase 3 summary drops the dedicated export/UAPI survey or the focused `zigux/tests/phase3_export_uapi_layout.zig` replay, repair that shared summary only. Do not use that as a reason to reopen the ABI header, unsafe, or low-level-wrapper packets.
