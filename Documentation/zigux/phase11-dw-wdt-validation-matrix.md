# Phase 11 DesignWare Watchdog Validation Matrix

This matrix keeps the current bounded validation packet for the Zigux
`dw_wdt` lane explicit.

## Status

- `PHASE11_DW_WDT_STATUS=hardware_validation_matrix_landed`
- current surveyed packet pin: `75f8336c4305beed127d7abfae37d3999b7cc57c`
- active watchdog continuity for this matrix and its coupled survey packet is
  `P11-L10`
- scope: keep the current `dw_wdt` starter honest about what is already
  reviewable, name the next kernel-facing checkpoint, and avoid overclaiming
  platform registration side effects, clock or reset wiring, IRQ delivery, or
  live MMIO behavior before those surfaces exist in Zigux

## Current Evidence

- `drivers/watchdog/dw_wdt.zig` keeps the starter logic, registration-facing
  handoff, and platform-registration scaffold summary reviewable.
- `drivers/watchdog/dw_wdt_verify.zig` keeps teardown and failure-mode parity
  reviewable.
- `drivers/watchdog/dw_wdt_pm.zig` keeps the bounded PM-helper handoff
  reviewable.
- `zigux/tests/phase11_dw_wdt_manifest.json` and
  `zigux/tests/phase11_dw_wdt_survey.zig` keep the lane-local packet fail
  closed on current-head truth.
- `Documentation/zigux/phase11-dw-wdt-survey.md` keeps the same packet summary
  readable for reviewers.

## Shared Gap And Next Step

- `zigux/tests/phase11_build.zig` is still a shared current-head gap rather
  than live lane evidence here.
- The next bounded same-lane follow-up remains the manifest-marked ready-next
  step: hardware-backed MMIO validation around suspend, resume, and
  platform-backed probe or remove execution, without widening into unrelated
  driver behavior.

## Non-Goals

- no claim that live platform registration side effects are already executing
- no claim that clock or reset acquisition, IRQ delivery, or hardware-backed
  MMIO validation has already landed
- no migration of this driver-local packet into a broader shared Phase 11
  reminder surface
