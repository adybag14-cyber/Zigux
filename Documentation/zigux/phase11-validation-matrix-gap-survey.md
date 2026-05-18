# Phase 11 Validation Matrix Gap Survey

This note records the roadmap-facing validation-matrix coverage for the current
Phase 11 simple-driver packet on `master`.

## Status

- `PHASE11_MATRIX_GAP_STATUS=hvc_matrix_direct_readback_only`
- lane: `P11-L03`
- reviewed against live `master`
- scope: verify the current driver-local matrix packet against the directly
  readable HVC matrix, the adjacent shared header-boundary matrix, and the
  narrowed HVC continuity inventory without reopening driver-local
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
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-build-inventory.py`
- `zigux/tests/fixtures/phase11_build_inventory.json`

Current direct contents reads in this run do not rematerialize
`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`,
`Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, or
`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, so the shared matrix
packet is no longer an honest four-matrix direct-readback claim.

The only directly readable driver-local Phase 11 matrix note on current
`master` is `Documentation/zigux/phase11-hvc-console-validation-matrix.md`.

`Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md` remains
useful adjacent shared evidence, but it is not one of the driver-local Phase 11
validation matrices named by the roadmap.

`zigux/tests/fixtures/phase11_build_inventory.json` still records the narrower
current-head HVC continuity packet: 4 HVC archival build test names, 3 shared
depend steps, 1 dedicated survey replay, and 2 proof adjunct replays. That
shared build inventory does not stand in for a whole-Phase-11 replay roster;
it now exists to keep the surviving HVC continuity packet explicit while the
other driver-local matrix notes remain missing on current `master`.

## Validation Gate

- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- `python3 scripts/zigux/check-phase11-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `python3 scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-build-inventory.py`

## Matrix Survey

- `bcm2835_wdt`: `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
  does not rematerialize on current `master`, so keep bcm2835 matrix coverage
  framed as a repo-reality gap rather than live reminder evidence.
- `gpio_wdt`: `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md` does
  not rematerialize on current `master`, so keep gpio matrix coverage framed as
  a repo-reality gap rather than live reminder evidence.
- `hvc_console`: `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
  is directly readable on current `master`, and the narrowed build inventory
  still keeps the HVC archival continuity packet explicit through
  `phase11-hvc-console-tests`, `phase11-hvc-console-verify-tests`,
  `phase11-hvc-cleanup-tests`, and `phase11-hvc-console-survey-tests`.
- `dw_wdt`: `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` does not
  rematerialize on current `master`, so the DesignWare matrix is again a
  repo-reality gap even though the narrower owner packet still survives through
  `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`,
  `zigux/tests/phase11_dw_wdt_manifest.json`, and
  `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`.

## Review Rules

- Treat this survey as current-head driver-local matrix truthfulness only, not
  as proof of full platform-backed closure for any Phase 11 driver lane.
- Do not use the surviving HVC matrix or the adjacent header-parity matrix to
  overclaim broader GPIO, watchdog, notifier, khvcd, sysrq, MMIO, or
  host-backed execution.
- If one or more missing driver-local matrix notes rematerialize later, update
  this survey and both matrix-gap checkers in the same bounded pass so the
  shared-packet description stays honest.
