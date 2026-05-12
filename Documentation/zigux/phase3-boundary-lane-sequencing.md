# Phase 3 Boundary Lane Sequencing

This note restores the shared owner map for the current Phase 3 ABI substrate packet on live `master`.

## Purpose

The active Phase 3 packet still spans a shared ABI summary, starter kernel relay, starter UAPI companions, Linux-facing header governance, Zigux-owned header-family follow-through, policy and unsafe rules, focused low-level wrapper proof, and validator-support helpers. Recent bounded runs already split those surfaces into separate substrate lanes, so this shared note must now route by owner and behavior class instead of treating the whole starter boundary as one packet or sending every `layout_assert.zig` change through the policy lane.

## Current lane map

- shared ABI and bindings packet, lane baseline `P3-X08`:
  - `Documentation/zigux/phase3-abi-slice.md`
  - `zigux/tests/fixtures/phase3_abi_manifest.json`
  - `include/zigux/abi.h`
  - `include/zigux/dev_t.h`
  - `zigux/bindings/abi.zig`
  - `zigux/bindings/dev_t.zig`
  - `zigux/bindings/notifier_abi.zig`
  - `zigux/helpers/layout_assert.zig`
  - `zigux/tests/phase3_abi.zig`
  - `zigux/tests/phase3_abi_dump.zig`
  - `scripts/zigux/check-phase3-abi.py`
  - `scripts/zigux/check-phase3-abi-dump-gate.py`
  - `scripts/zigux/survey-phase3-abi-constant-parity.py`
- kernel-facing relay packet, lane `P3-Y07`:
  - `Documentation/zigux/phase3-kernel-export-shim-governance.md`
  - `zigux/kernel/export_shim.zig`
- starter UAPI packet, lane `P3-Y02`:
  - `Documentation/zigux/phase3-export-uapi-boundary-survey.md`
  - `zigux/uapi/version.zig`
  - `zigux/uapi/dev_t.zig`
  - `scripts/zigux/validate-phase3-export-uapi-survey.py`
- Linux-facing aggregation-header packet, lane `P3-Y05`:
  - `Documentation/zigux/phase3-linux-zigux-header-governance.md`
  - `include/linux/zigux.h`
- Zigux-owned ABI header-family packet, lane `P3-Y06`:
  - `Documentation/zigux/phase3-abi-header-family-survey.md`
  - `Documentation/zigux/phase3-abi-h-boundary-next-step.md`
  - `include/zigux/abi.h`
  - `include/zigux/dev_t.h`
  - `zigux/bindings/abi.zig`
  - `zigux/bindings/dev_t.zig`
  - `zigux/bindings/notifier_abi.zig`
  - `scripts/zigux/validate-phase3-abi-bindings-syntax.py`
- policy and unsafe packet, lane `P3-Y04`:
  - `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md`
  - `zigux/helpers/panic_policy.zig`
  - `zigux/helpers/allocator_policy.zig`
  - the policy-admission surfaces inside `zigux/helpers/mmio.zig`
  - `zigux/unsafe/narrow.zig`
  - `scripts/zigux/check-phase3-policy-byte-guards.py`
  - `scripts/zigux/check-phase3-policy-unsafe-focused-replay.py`
  - `scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py`
  - `scripts/zigux/validate-phase3-policy-unsafe-survey.py`
- low-level wrapper packet, lane `P3-Y03`:
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
  - `scripts/zigux/phase3_catalog.py`
  - `scripts/zigux/phase3_check_lib.py`
  - `scripts/zigux/generate-phase3-check-wrappers.py`
  - `scripts/zigux/run-phase3-checks.py`

## Ownership split

- shared ABI and bindings owns manifest-backed packet accounting, the broad ABI slice summary, `layout_assert.zig` layout-entrypoint truth, ABI constant-parity drift, dump-gate wording, and shared binding or header-lift truthfulness that affects the whole substrate packet
- kernel-facing relay owns only the `zigux/kernel/export_shim.zig` governance note and kernel-side relay wording; it does not absorb starter UAPI, Linux-facing header, or Zigux-owned header-family follow-through
- starter UAPI owns the bounded `zigux/uapi/version.zig` and `zigux/uapi/dev_t.zig` companions plus the survey wording that explains they are still exercised through the shared Phase 3 build, dump, and interop routes
- Linux-facing aggregation-header ownership stays with `include/linux/zigux.h` and its dedicated governance note; it does not own canonical ABI layout or the starter UAPI companion wording
- Zigux-owned ABI header family owns `include/zigux/abi.h`, `include/zigux/dev_t.h`, and the curated binding mirrors plus the dedicated next-step note that keeps same-family syntax, layout-survey, and truthfulness follow-through bounded
- policy and unsafe owns panic-mode, allocator-mode, unsafe-scope, and MMIO interop-policy admission drift, including the typed and byte-policy relays that decide whether callers may cross into the narrow unsafe surface
- low-level wrapper owns direct MMIO ranges and read or write behavior, width coverage, alignment rules, odd-offset behavior, atomic behavior, barrier behavior, and the focused replay wording that proves those direct low-level helpers
- validator-support owns shared scripts-root, docs-sync, self-test, catalog, wrapper-generation, and runner-route truthfulness for the current Phase 3 packet without claiming helper, kernel, or header behavior on its own

## Anti-overlap rules

- do not route `zigux/helpers/mmio.zig` by file path alone; route it by behavior class instead
- do not route `zigux/helpers/layout_assert.zig` by file path alone either; if the drift is about struct layouts, exported constants, helper entrypoints consumed by the shared ABI packet, or `survey-phase3-abi-constant-parity.py`, keep it in the shared ABI and bindings packet
- if the drift is about panic-mode decoding, allocator-mode decoding, unsafe-scope bytes, typed policy relays, MMIO interop-policy admission, or the policy-and-unsafe survey wording, keep it in the policy and unsafe packet
- if the drift is about direct MMIO reads or writes, width, alignment, odd offsets, atomic behavior, barrier behavior, or the focused low-level replay wording, keep it in the low-level wrapper packet
- if the drift is about `zigux/kernel/export_shim.zig` relay ownership, keep it in the kernel-facing relay packet even when the starter UAPI survey also names the file
- if the drift is about `zigux/uapi/version.zig`, `zigux/uapi/dev_t.zig`, the starter-boundary survey wording, or whether the starter packet still points at the shared replay routes instead of retired export/UAPI-only replays, keep it in the starter UAPI packet
- if the drift is about `include/linux/zigux.h` aggregation or Linux-facing header governance, keep it in the Linux-facing aggregation-header packet
- if the drift is about `include/zigux/abi.h`, `include/zigux/dev_t.h`, curated bindings, header-family syntax guards, or the dedicated same-family next-step note, keep it in the Zigux-owned ABI header-family packet
- if the drift is about manifest accounting, broad ABI summary wording, shared dump or compile routes, or shared binding truthfulness that touches more than one substrate family, keep it in the shared ABI and bindings packet
- if the drift is about `scripts/zigux/README.md`, `zigux/Makefile`, self-test routes, wrapper generation, catalog discovery, or shared validator entrypoints, keep it in the validator-support packet

## Current bounded rule

This note is the shared substrate owner map only. It does not claim a new helper family, another replay tranche, or broader kernel-port progress. Future Phase 3 follow-up should reopen one packet only using the split above, with `P3-X11` reserved for shared closure, ledger, or lane-state corrections when the owner map itself drifts and the packet-local lanes remain otherwise accurate.
