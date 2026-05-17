# Phase 11 Validation Matrix Gap Survey

This note records the roadmap-facing validation-matrix coverage for the current
Phase 11 simple-driver packet on `master`.

## Status

- `PHASE11_MATRIX_GAP_STATUS=direct_readback_matrix_drift_recorded`
- lane: `P11-L05`
- reviewed against live `master`
- scope: compare the Phase 11 roadmap anchors against the current validation-matrix
  packet without reopening driver-local implementation, DesignWare
  platform-registration follow-through, or HVC cleanup-alignment checker repair

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
- `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`
- `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md`
- `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`
- `scripts/zigux/check-phase11-matrix-gap-survey.py`

Current direct contents reads in this run did not rematerialize
`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`,
`Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`,
`Documentation/zigux/phase11-hvc-console-validation-matrix.md`, or
`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, so the shared matrix
packet is no longer an honest four-matrix direct-readback claim.

The current HVC survey note already keeps the HVC archival packet inventory-backed
when those direct matrix and companion surfaces do not rematerialize in the same
readback pass.

## Validation Gate

- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- `python3 scripts/zigux/check-phase11-matrix-gap-survey.py`

## Gap Survey

- `bcm2835_wdt`: the validation matrix did not rematerialize by current direct
  contents readback in this run, so keep older bcm2835 matrix claims archival
  rather than presenting them as live direct-readback evidence.
- `gpio_wdt`: the validation matrix did not rematerialize by current direct
  contents readback in this run, so keep the gpio matrix packet inventory-backed
  until a future reread confirms the file again.
- `hvc_console`: `Documentation/zigux/phase11-hvc-console-survey.md` already
  records that direct contents reads did not rematerialize
  `Documentation/zigux/phase11-hvc-console-validation-matrix.md` or the direct
  companion packet, so HVC matrix continuity is inventory-backed rather than
  direct-readback current-head evidence.
- `dw_wdt`: current continuity notes still keep DesignWare follow-through explicit
  through `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md` and
  `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`, but the
  validation matrix itself did not rematerialize by direct contents readback in
  this run and should not be counted as a live direct-readback matrix until a
  future reread confirms it again.

## Review Rules

- Treat this survey as current-head matrix truthfulness only, not as proof that
  the missing matrix files are gone forever or that any driver-local packet has
  been reopened.
- Do not claim four live driver-local validation matrices on current `master`
  while current direct readback still fails to rematerialize those matrix files.
- If future direct contents reads confirm any Phase 11 matrix again, update this
  survey and `scripts/zigux/check-phase11-matrix-gap-survey.py` in the same patch
  so the direct-readback count stays honest.
