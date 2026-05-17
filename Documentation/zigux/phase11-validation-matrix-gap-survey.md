# Phase 11 Validation Matrix Gap Survey

This note records the roadmap-facing validation-matrix coverage for the current
Phase 11 simple-driver packet on `master`.

## Status

- `PHASE11_MATRIX_GAP_STATUS=driver_local_matrix_docs_absent_shared_header_matrix_only`
- lane: `P11-L03`
- reviewed against live `master`
- scope: verify the current driver-local matrix packet against the directly
  readable docs-root and build-inventory evidence without reopening driver-local
  implementation, DesignWare continuity, or HVC cleanup-alignment follow-through

## Roadmap Anchor

- Phase 11 still names `drivers/watchdog/gpio_wdt.c`,
  `drivers/watchdog/bcm2835_wdt.c`, `drivers/watchdog/dw_wdt.c`, and
  `drivers/tty/hvc/hvc_console.c` as the simple-production-driver anchors.
- Phase 11 still requires a hardware validation matrix together with teardown or
  failure-mode parity.

## Current Repo Reality

- `Documentation/zigux/phase11-validation-matrix-gap-survey.md`
- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md`
- `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`
- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-build-inventory.py`
- `zigux/tests/fixtures/phase11_build_inventory.json`

Current direct contents reads in this run did not rematerialize
`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`,
`Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`,
`Documentation/zigux/phase11-hvc-console-validation-matrix.md`, or
`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, so the shared
matrix packet is no longer an honest four-matrix direct-readback claim.

The only directly readable Phase 11 matrix note on current `master` is
`Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`.
That shared header-boundary matrix remains useful adjacent evidence, but it is
not a substitute for the missing driver-local watchdog and HVC validation
matrices.

`zigux/tests/fixtures/phase11_build_inventory.json` still records 14 build test
names, 13 shared depend steps, and one dedicated survey replay
(`zigux/tests/phase11_hvc_console_survey.zig`), so the surviving build-backed
review packet still points at driver-local proof files even while the docs-root
driver-local matrix notes remain absent.

## Validation Gate

- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- `python3 scripts/zigux/check-phase11-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `python3 scripts/zigux/check-phase11-validation-matrix-gap-survey.py`

## Gap Survey

- `bcm2835_wdt`: `phase11_build_inventory.json` still carries
  `phase11-bcm2835-wdt-tests`, `phase11-bcm2835-wdt-verify-tests`, and
  `phase11-bcm2835-wdt-survey-tests`, but no current
  `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md` is directly
  readable on `master`.
- `gpio_wdt`: `phase11_build_inventory.json` still carries
  `phase11-gpio-wdt-tests` and `phase11-gpio-wdt-survey-tests`, but no current
  `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md` is directly
  readable on `master`.
- `hvc_console`: `phase11_build_inventory.json` still carries
  `phase11-hvc-console-tests`, `phase11-hvc-console-verify-tests`,
  `phase11-hvc-cleanup-tests`, and `phase11-hvc-console-survey-tests`, while
  `Documentation/zigux/phase11-hvc-console-survey.md` explicitly records that
  `Documentation/zigux/phase11-hvc-console-validation-matrix.md` did not
  rematerialize in this run.
- `dw_wdt`: `phase11_build_inventory.json` still carries
  `phase11-dw-wdt-tests`, `phase11-dw-wdt-registration-scaffold-tests`,
  `phase11-dw-wdt-verify-tests`, and `phase11-dw-wdt-survey-tests`, but the
  directly readable DesignWare docs packet remains the continuity pair
  `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md` and
  `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md` rather than a
  live `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`.

## Review Rules

- Treat this survey as current-head driver-local matrix truthfulness only, not
  as proof of full platform-backed closure for any Phase 11 driver lane.
- Do not use the surviving build inventory or the shared UAPI header matrix to
  overclaim current driver-local watchdog or HVC matrix coverage.
- If one of the four driver-local matrix notes rematerializes later, update this
  survey and both matrix-gap checkers in the same patch so the direct-readback
  claim stays honest.
