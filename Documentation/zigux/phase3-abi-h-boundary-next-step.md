# Phase 3 ABI H Boundary Next Step

This note records the next bounded same-lane follow-through for the Zigux-owned
`include/zigux/abi.h` family after the landed header-family survey.

## Current landed surface

- `Documentation/zigux/phase3-abi-header-family-survey.md`
- `Documentation/zigux/phase3-export-uapi-boundary-survey.md`
- `Documentation/zigux/phase3-linux-zigux-header-governance.md`
- `include/linux/zigux.h`
- `include/zigux/abi.h`
- `include/zigux/dev_t.h`
- `zigux/bindings/abi.zig`
- `zigux/kernel/export_shim.zig`
- `zigux/uapi/version.zig`
- `zigux/tests/phase3_export_uapi.zig`
- `zigux/tests/phase3_export_uapi_layout.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `scripts/zigux/validate-phase3-abi-header-family-survey.py`
- `scripts/zigux/validate-phase3-abi-bindings-syntax.py`
- `scripts/zigux/survey-phase3-abi-constant-parity.py`
- `make -C zigux phase3-validate`
- `make -C zigux phase3`

## Next bounded step

- keep same-lane follow-through here limited to one header-family truthfulness,
  syntax-guard, or layout-survey adjustment at a time
- `scripts/zigux/survey-phase3-abi-constant-parity.py` now holds two exact
  nested chrdev ack-window policy budget view-plus-summary footholds across
  `include/zigux/abi.h` and `zigux/bindings/abi.zig`; keep extending that
  family one bounded sibling pair at a time instead of widening into another
  packet
- if `include/zigux/abi.h` grows, update `zigux/bindings/abi.zig`,
  `include/zigux/dev_t.h`, or `zigux/uapi/version.zig`, and the export or UAPI
  replay packet together instead of widening into unrelated helper work
- treat `scripts/zigux/validate-phase3-abi-header-family-survey.py` and
  `scripts/zigux/validate-phase3-abi-bindings-syntax.py` as the first review
  gates before broader ABI slice follow-through reopens
- keep broad shared reminders honest whenever they name the header-family packet

## Non-goals

- no new exported header family claims
- no runtime-loader or helper-lane expansion
- no deep-core include-tree migration beyond the shipped export and UAPI surface
