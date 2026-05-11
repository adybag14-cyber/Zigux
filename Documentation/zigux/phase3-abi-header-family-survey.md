# Phase 3 ABI Header Family Survey

This note records the current Zigux-owned header-family review surface inside the
active Phase 3 ABI and interop packet.

## Current packet

- `include/linux/zigux.h`
- `include/zigux/abi.h`
- `include/zigux/dev_t.h`
- `zigux/bindings/abi.zig`
- `zigux/kernel/export_shim.zig`
- `zigux/uapi/version.zig`
- `zigux/uapi/dev_t.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c`
- `zigux/tests/fixtures/phase3_abi/expected.json`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `scripts/zigux/validate-phase3-abi-bindings-syntax.py`
- `scripts/zigux/survey-phase3-abi-constant-parity.py`
- `zigux/Makefile`
- `make -C zigux phase3-validate`
- `make -C zigux phase3`

## Review boundary

- keep the exported Linux-facing header family bounded to `include/linux/zigux.h`
  and the Zigux-owned UAPI family bounded to `include/zigux/abi.h` plus the
  canonical `include/zigux/dev_t.h` starter companion
- keep same-lane follow-through here inside note, syntax-guard, or layout-survey
  work unless a real exported field family changes
- treat `zigux/bindings/abi.zig`, `zigux/kernel/export_shim.zig`,
  `zigux/uapi/version.zig`, and `zigux/uapi/dev_t.zig` as the current
  implementation-facing companions for that header-family boundary while the
  starter UAPI surface remains a bounded version-plus-dev_t pair

## Non-goals

- no new exported header family claims
- no runtime-loader or helper-lane expansion
- no deep-core header migration beyond the shipped export and UAPI surface

## Shared reminder

Broad Phase 3 summaries that name the export and UAPI boundary or the ABI
constant-parity packet should keep this survey explicit beside
`Documentation/zigux/phase3-export-uapi-boundary-survey.md`,
`Documentation/zigux/phase3-linux-zigux-header-governance.md`,
`Documentation/zigux/phase3-abi-h-boundary-next-step.md`,
`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`,
`scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/uapi/dev_t.zig`,
`zigux/bindings/abi.zig`, `zigux/tests/phase3_abi_dump.zig`,
`zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c`,
`zigux/tests/fixtures/phase3_abi/expected.json`,
`scripts/zigux/validate-phase3-export-uapi-survey.py`,
`scripts/zigux/validate-phase3-abi-bindings-syntax.py`, and
`scripts/zigux/survey-phase3-abi-constant-parity.py`; the narrower
`include/zigux/dev_t.h` plus `zigux/uapi/version.zig` starter-companion detail
should stay anchored in this dedicated survey and the paired next-step note
instead of being treated as a required broad-summary repeat everywhere.
