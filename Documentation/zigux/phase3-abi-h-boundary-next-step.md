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
- `zigux/uapi/dev_t.zig`
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
  `include/zigux/dev_t.h`, `zigux/uapi/version.zig`, `zigux/uapi/dev_t.zig`,
  and the shared ABI reminder packet together; only add a new `zigux/uapi/*`
  companion when that companion lands with its own bounded export or UAPI
  packet instead of letting the shared reminder surfaces get ahead of the tree
- treat `scripts/zigux/validate-phase3-abi-header-family-survey.py` and
  `scripts/zigux/validate-phase3-abi-bindings-syntax.py` as the first review
  gates before broader ABI slice follow-through reopens
- keep broad shared reminders honest whenever they name the header-family
  packet, including the current `zigux/uapi/version.zig` and
  `zigux/uapi/dev_t.zig` starter companions beside the dedicated survey and
  next-step notes

## Non-goals

- no new exported header family claims
- no runtime-loader or helper-lane expansion
- no deep-core include-tree migration beyond the shipped export and UAPI surface
