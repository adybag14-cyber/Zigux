# Phase 3 Validator Support Surface

This note records the current shared validator-support packet inside the active
Phase 3 ABI and runtime tranche.

## Current packet

- `scripts/zigux/validate-phase3.py`
- `scripts/zigux/validate_phase3_selftest.py`
- `scripts/zigux/check-phase3-selftest-surface.py`
- `scripts/zigux/check-phase3-readme-tooling-inventory.py`
- `scripts/zigux/check-phase3-catalog-selftest.py`
- `scripts/zigux/check-phase3-abi-dump-gate.py`
- `scripts/zigux/validate-phase3-policy-unsafe-survey.py`
- `scripts/zigux/check-phase3-policy-byte-guards.py`
- `scripts/zigux/check-phase3-policy-unsafe-focused-replay.py`
- `scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py`
- `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `scripts/zigux/validate-phase3-abi-header-family-survey.py`
- `scripts/zigux/validate-phase3-validator-support-surface.py`
- `scripts/zigux/validate-phase3-abi-bindings-syntax.py`
- `scripts/zigux/survey-phase3-abi-constant-parity.py`
- `scripts/zigux/phase3_catalog.py`
- `scripts/zigux/phase3_check_lib.py`
- `scripts/zigux/generate-phase3-check-wrappers.py`
- `scripts/zigux/run-phase3-checks.py`
- `Documentation/zigux/phase3-abi-slice.md`
- `Documentation/zigux/phase3-boundary-lane-sequencing.md`
- `Documentation/zigux/phase3-kernel-export-shim-governance.md`
- `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md`
- `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`
- `Documentation/zigux/phase3-export-uapi-boundary-survey.md`
- `Documentation/zigux/phase3-linux-zigux-header-governance.md`
- `Documentation/zigux/phase3-abi-header-family-survey.md`
- `Documentation/zigux/phase3-abi-h-boundary-next-step.md`
- `zigux/uapi/dev_t.zig`
- `zigux/bindings/abi.zig`
- `zigux/Makefile`
- `python3 scripts/zigux/phase3_catalog.py --self-test`
- `python3 scripts/zigux/phase3_catalog.py --audit-doc-sync`
- `python3 scripts/zigux/phase3_check_lib.py --self-test`
- `python3 scripts/zigux/generate-phase3-check-wrappers.py --self-test`
- `python3 scripts/zigux/generate-phase3-check-wrappers.py --check`
- `python3 scripts/zigux/run-phase3-checks.py --self-test`
- `python3 scripts/zigux/run-phase3-checks.py --slug abi`
- `make -C zigux phase3-validate`
- `make -C zigux phase3-selftest`
- `make -C zigux phase3`

## Review boundary

- keep same-lane follow-through here inside validator-support, catalog,
  wrapper-audit, or docs-truthfulness work unless a real Phase 3 ABI surface
  changes
- treat `phase3_catalog.py`, `phase3_check_lib.py`, `generate-phase3-check-wrappers.py`,
  and `run-phase3-checks.py` as shipped helper entrypoints on current `master`,
  not as historical-only references
- keep `Documentation/zigux/phase3-validator-support-surface.md` paired with
  `scripts/zigux/validate-phase3-validator-support-surface.py`,
  `Documentation/zigux/phase3-kernel-export-shim-governance.md`, and
  `Documentation/zigux/phase3-abi-h-boundary-next-step.md` so the shipped
  validator-support inventory and the broad next-step reminder policy fail
  closed together when either note drifts
- keep `make -C zigux phase3-selftest` as a focused companion route that
  complements but does not duplicate the default `make -C zigux phase3-validate`
  packet

## Non-goals

- no new ABI field-family claims
- no runtime-loader or helper-lane expansion outside the existing Phase 3 packet
- no deep-core port claims beyond the shipped ABI and interop support surface

## Shared reminder

Broad Phase 3 summaries that name the validator-support packet should keep this
note explicit beside `scripts/zigux/README.md`, `zigux/tests/README.md`,
`scripts/zigux/validate_phase3_selftest.py`,
`scripts/zigux/validate-phase3-validator-support-surface.py`,
`Documentation/zigux/phase3-kernel-export-shim-governance.md`,
`Documentation/zigux/phase3-abi-header-family-survey.md`,
`Documentation/zigux/phase3-abi-h-boundary-next-step.md`,
`Documentation/zigux/review-checklist.md`,
`Documentation/zigux/phase3-policy-unsafe-boundary-survey.md`,
`scripts/zigux/check-phase3-policy-unsafe-focused-replay.py`,
`scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py`,
`zigux/uapi/dev_t.zig`, `zigux/bindings/abi.zig`, and
`make -C zigux phase3-selftest`; adjacent header-family and checklist reminders
should keep `include/zigux/dev_t.h`, `zigux/uapi/version.zig`, and
`zigux/uapi/dev_t.zig` explicit as the bounded starter-companion policy without
dropping the dedicated policy-and-unsafe replay checks or restating this
validator-support note as if those shipped support helpers were historical-only
entrypoints.
