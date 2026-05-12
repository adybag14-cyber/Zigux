# Phase 3 Boundary Lane Sequencing

This note restores the shared owner map for the current Phase 3 ABI substrate packet on live `master`.

## Purpose

The active Phase 3 packet already spans a shared ABI summary, starter kernel relay, starter export and UAPI companions, policy and unsafe rules, focused low-level wrapper proof, and validator-support helpers. The starter boundary packet now also includes a dedicated kernel-facing governance note for `zigux/kernel/export_shim.zig`, so the `zigux/kernel/` side of the boundary no longer shares ownership implicitly with the starter UAPI and Linux-facing header surfaces. This note keeps those surfaces reviewable as separate bounded packets so nearby runs do not reopen the same drift from two directions.

## Current packet families

- shared ABI and bindings packet:
  - `Documentation/zigux/phase3-abi-slice.md`
  - `zigux/tests/fixtures/phase3_abi_manifest.json`
  - `include/zigux/abi.h`
  - `include/zigux/dev_t.h`
  - `zigux/bindings/abi.zig`
  - `zigux/bindings/dev_t.zig`
  - `zigux/bindings/notifier_abi.zig`
  - `zigux/tests/phase3_abi.zig`
  - `zigux/tests/phase3_abi_dump.zig`
- kernel-facing starter boundary packet:
  - `Documentation/zigux/phase3-kernel-export-shim-governance.md`
  - `Documentation/zigux/phase3-export-uapi-boundary-survey.md`
  - `Documentation/zigux/phase3-linux-zigux-header-governance.md`
  - `Documentation/zigux/phase3-abi-header-family-survey.md`
  - `Documentation/zigux/phase3-abi-h-boundary-next-step.md`
  - `include/linux/zigux.h`
  - `zigux/kernel/export_shim.zig`
  - `zigux/uapi/version.zig`
  - `zigux/uapi/dev_t.zig`
  - `scripts/zigux/validate-phase3-export-uapi-survey.py`
- policy and unsafe packet:
  - `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md`
  - `zigux/helpers/layout_assert.zig`
  - `zigux/helpers/panic_policy.zig`
  - `zigux/helpers/allocator_policy.zig`
  - `zigux/unsafe/narrow.zig`
  - the policy-admission surfaces inside `zigux/helpers/mmio.zig`
  - `scripts/zigux/check-phase3-policy-byte-guards.py`
- low-level wrapper packet:
  - `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`
  - `zigux/helpers/atomic.zig`
  - `zigux/helpers/barrier.zig`
  - the direct range and raw access surfaces inside `zigux/helpers/mmio.zig`
  - `zigux/tests/phase3_low_level_wrappers_build.zig`
  - `zigux/tests/phase3_low_level_wrappers.zig`
  - `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`
- validator-support packet:
  - `Documentation/zigux/phase3-validator-support-surface.md`
  - `scripts/zigux/validate-phase3.py`
  - `scripts/zigux/validate_phase3_selftest.py`
  - `scripts/zigux/check-phase3-selftest-surface.py`
  - `scripts/zigux/check-phase3-readme-tooling-inventory.py`
  - `scripts/zigux/check-phase3-catalog-selftest.py`
  - `scripts/zigux/check-phase3-abi-dump-gate.py`
  - `scripts/zigux/validate-phase3-validator-support-surface.py`
  - `scripts/zigux/phase3_catalog.py`
  - `scripts/zigux/phase3_check_lib.py`
  - `scripts/zigux/generate-phase3-check-wrappers.py`
  - `scripts/zigux/run-phase3-checks.py`

## Ownership split

- shared ABI and bindings owns manifest-backed packet accounting, the broad ABI slice summary, compile and dump route wording, and shared binding or header-lift truthfulness that affects the whole substrate packet
- kernel-facing starter boundary owns the dedicated export-shim governance note, the starter-boundary wording for `zigux/kernel/export_shim.zig`, `zigux/uapi/version.zig`, `zigux/uapi/dev_t.zig`, and `include/linux/zigux.h`, the packet-local `validate-phase3-export-uapi-survey.py` checker, and the survey wording that tells reviewers this starter packet is currently exercised through the shared `phase3-test`, `phase3-dump`, and `phase3-interop` routes rather than through a dedicated export/UAPI-only replay family
- policy and unsafe owns interop-policy admission drift, reserved-byte or typed-policy decoding drift, and the narrow unsafe-scope boundary, including `allowsInteropPolicy*`, `requireInteropPolicy*`, `rangeInteropPolicy*`, and `read*InteropPolicy*` or `write*InteropPolicy*` MMIO policy relays
- low-level wrapper owns direct helper-surface, focused build-route, and focused replay drift for atomic, barrier, and MMIO behavior, including `range()`, direct `read*()` and `write*()` accessors, width coverage, alignment rules, odd-offset behavior, and the directly coupled focused replay wording
- validator-support owns shared scripts-root, docs-sync, self-test, catalog, wrapper-generation, and runner-route truthfulness for the current Phase 3 packet without claiming helper or header behavior on its own

## Anti-overlap rules

- do not route `zigux/helpers/mmio.zig` by file path alone; route it by behavior class instead
- if the drift is about policy admission, interop-policy decoding, unsafe-scope bytes, or typed policy relays, keep it in the policy and unsafe packet
- if the drift is about direct MMIO reads or writes, width, alignment, odd offsets, atomic behavior, barrier behavior, or focused replay wording, keep it in the low-level wrapper packet
- if the drift is about kernel-facing export-shim relay ownership, starter UAPI truth, Linux-facing header governance, the packet-local export/UAPI survey checker, or whether the starter packet still points at the shared replay routes instead of retired dedicated export/UAPI-only replays, keep it in the kernel-facing starter boundary packet
- if the drift is about manifest accounting, ABI summary wording, shared dump or compile routes, or broad binding truthfulness, keep it in the shared ABI packet
- if the drift is about `scripts/zigux/README.md`, `zigux/Makefile`, self-test routes, wrapper generation, catalog discovery, or shared validator entrypoints, keep it in the validator-support packet

## Current bounded rule

This note is the shared owner map only. It does not claim a new helper family, a dedicated extra replay lane, or broader kernel-port progress. Future Phase 3 follow-up should reopen one packet only, using the split above, unless a real shared substrate surface moves in more than one family at the same time.
