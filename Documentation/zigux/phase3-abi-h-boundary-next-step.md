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
- `zigux/bindings/dev_t.zig`
- `zigux/helpers/layout_assert.zig`
- `zigux/kernel/export_shim.zig`
- `zigux/uapi/version.zig`
- `zigux/uapi/dev_t.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c`
- `zigux/tests/fixtures/phase3_abi/expected.json`
- `zigux/tests/fixtures/phase3_abi_manifest.json`
- `scripts/zigux/check-phase3-abi.py`
- `python3 scripts/zigux/run-phase3-checks.py --slug abi`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `scripts/zigux/validate-phase3-abi-header-family-survey.py`
- `scripts/zigux/validate-phase3-abi-bindings-syntax.py`
- `scripts/zigux/survey-phase3-abi-constant-parity.py`
- `make -C zigux phase3-validate`
- `make -C zigux phase3`

## Next bounded step

- keep same-lane follow-through here limited to one header-family truthfulness,
  syntax-guard, or layout-survey adjustment at a time
- `scripts/zigux/survey-phase3-abi-constant-parity.py` now holds four exact
  nested chrdev ack-window policy budget family constants, four direct
  header-and-binding type markers, the dedicated
  `zigux/helpers/layout_assert.zig` three-`u32` helper quartet, and the
  committed dump, C harness, and expected-fixture keys across
  `include/zigux/abi.h`, `zigux/bindings/abi.zig`,
  `zigux/helpers/layout_assert.zig`, `zigux/tests/phase3_abi_dump.zig`,
  `zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c`, and
  `zigux/tests/fixtures/phase3_abi/expected.json`; keep extending that
  header-family survey one bounded sibling family at a time instead of
  widening into another packet
- the shared review checklist now carries an explicit Phase 3 header-family
  prompt; keep `Documentation/zigux/review-checklist.md`,
  `Documentation/zigux/phase3-abi-header-family-survey.md`,
  `include/zigux/dev_t.h`, and the paired starter-companion policy aligned
  there whenever the bounded header-family packet moves without implying a
  broader exported UAPI family
- if `include/zigux/abi.h` grows, refresh `zigux/bindings/abi.zig`,
  `zigux/tests/phase3_abi.zig`, `zigux/tests/phase3_abi_dump.zig`,
  `zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c`,
  `zigux/tests/fixtures/phase3_abi/expected.json`,
  `zigux/tests/fixtures/phase3_abi_manifest.json`, the paired starter
  companions, and the shared ABI reminder packet together; only add a new
  `zigux/uapi/*` companion when that companion lands with its own bounded
  export or UAPI packet instead of letting the shared reminder surfaces get
  ahead of the tree
- treat `scripts/zigux/check-phase3-abi.py`,
  `scripts/zigux/survey-phase3-abi-constant-parity.py`,
  `python3 scripts/zigux/run-phase3-checks.py --slug abi`,
  `scripts/zigux/validate-phase3-abi-header-family-survey.py`, and
  `scripts/zigux/validate-phase3-abi-bindings-syntax.py` as the first review
  gates before broader ABI slice follow-through reopens
- keep broad shared reminders honest whenever they name the header-family
  packet, keeping `zigux/uapi/dev_t.zig` explicit beside the dedicated survey
  and next-step notes while leaving the narrower `zigux/uapi/version.zig`
  starter-companion detail anchored here, beside the direct replay files,
  focused validator, focused checker, and manifest-backed ABI packet, and in
  `Documentation/zigux/phase3-abi-header-family-survey.md` unless the broader
  export/UAPI packet actually grows
- the next shared reminder follow-through is `scripts/zigux/README.md`: its
  Phase 3 header-family line still trails the dedicated survey by collapsing the
  starter companion wording to the already-named Zig-side foothold, so refresh
  that scripts-root reminder before widening any broader Phase 3 summary work

## Non-goals

- no new exported header family claims
- no runtime-loader or helper-lane expansion
- no deep-core include-tree migration beyond the shipped export and UAPI surface
