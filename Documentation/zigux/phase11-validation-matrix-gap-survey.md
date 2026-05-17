# Phase 11 Validation Matrix Gap Survey

This note records the roadmap-facing validation-matrix coverage for the current
Phase 11 simple-driver packet on `master`.

## Status

- `PHASE11_MATRIX_GAP_STATUS=four_matrix_direct_readback_restored`
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
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-build-inventory.py`
- `zigux/tests/fixtures/phase11_build_inventory.json`

Current direct contents reads in this run do rematerialize
`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`,
`Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`,
`Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and
`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, so the shared
matrix packet is once again an honest four-matrix direct-readback claim.

`Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md` remains
useful adjacent shared evidence, but it is not one of the four driver-local
Phase 11 matrices restored by current direct readback.

`zigux/tests/fixtures/phase11_build_inventory.json` still records 14 build test
names, 13 shared depend steps, and one dedicated survey replay
(`zigux/tests/phase11_hvc_console_survey.zig`), so the shared build-backed
review packet continues to point at the same watchdog and HVC replay families
that the four driver-local matrix notes summarize.

## Validation Gate

- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- `python3 scripts/zigux/check-phase11-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `python3 scripts/zigux/check-phase11-validation-matrix-gap-survey.py`

## Matrix Survey

- `bcm2835_wdt`: `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
  is directly readable on current `master`, matching the build inventory's
  `phase11-bcm2835-wdt-tests`, `phase11-bcm2835-wdt-verify-tests`, and
  `phase11-bcm2835-wdt-survey-tests` coverage.
- `gpio_wdt`: `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md` is
  directly readable on current `master`, matching the build inventory's
  `phase11-gpio-wdt-tests` and `phase11-gpio-wdt-survey-tests` coverage.
- `hvc_console`: `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
  is directly readable on current `master`, matching the build inventory's
  `phase11-hvc-console-tests`, `phase11-hvc-console-verify-tests`,
  `phase11-hvc-cleanup-tests`, and `phase11-hvc-console-survey-tests`
  coverage.
- `dw_wdt`: `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` is
  directly readable on current `master`, matching the build inventory's
  `phase11-dw-wdt-tests`, `phase11-dw-wdt-registration-scaffold-tests`,
  `phase11-dw-wdt-verify-tests`, and `phase11-dw-wdt-survey-tests` coverage.

## Review Rules

- Treat this survey as current-head driver-local matrix truthfulness only, not
  as proof of full platform-backed closure for any Phase 11 driver lane.
- Do not use the restored four-matrix readback to overclaim live GPIO, watchdog,
  notifier, khvcd, sysrq, MMIO, or host-backed execution.
- If one of the four driver-local matrix notes disappears again later, update
  this survey and both matrix-gap checkers in the same patch so the
  direct-readback claim stays honest.
