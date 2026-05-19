# Phase 11 GPIO Watchdog Validation Matrix

This document records the bounded gpio watchdog validation matrix for the current
Zigux Phase 11 simple-driver packet.

## Status

- `PHASE11_GPIO_WDT_STATUS=direct_readback_docs_packet_truthful`
- lane: `P11-L04`
- reviewed against live `master`
- scope: keep the current gpio watchdog teardown and failure-mode packet honest
  without widening into live GPIO descriptor acquisition, platform-driver
  registration, watchdog-core registration, remove hooks, reboot-backed teardown
  execution, or hardware-backed validation

## Current Repo Reality

The directly readable gpio watchdog matrix packet on current `master` is:

- `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
- `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`

Current direct contents reads in this run do not rematerialize
`drivers/watchdog/gpio_wdt.zig`,
`zigux/tests/phase11_gpio_wdt.zig`,
`zigux/tests/phase11_gpio_wdt_platform_drvdata.zig`,
`zigux/tests/phase11_gpio_wdt_manifest.json`,
`zigux/tests/phase11_gpio_wdt_survey.zig`,
`Documentation/zigux/phase11-gpio-wdt-survey.md`,
`Documentation/zigux/phase11-shared-replay-contract.md`, or
`zigux/tests/phase11_build.zig`, so this matrix can no longer present those
surfaces as current direct-readback packet members.

## Current Direct-Readback Matrix

Treat the current gpio watchdog matrix packet as the narrower docs-only packet
below:

- `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
- `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`

The returned module slice and teardown note still keep the bounded
`descriptorRequestSummary()`, `platformDrvdataCheckpointSummary()`,
`nowayoutPolicySummary()`, `registrationHandoffSummary()`,
`registrationPlanSummary()`, `registerDeviceCallSummary()`,
`registerDeviceFailureSummary()`, `requestStop()`, and `summarizeTeardown()`
checkpoint names reviewable as documentation-backed teardown and failure-mode
surfaces.

## Teardown And Failure-Mode Review Surface

- teardown handoff: `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
  keeps the bounded stop-request split, register-device failure cues, and
  teardown ownership explicit without claiming remove-hook or reboot-backed
  shutdown execution.
- failure-mode packet: `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
  keeps the descriptor, drvdata-ordering, registration-plan, register-device,
  and teardown checkpoint names explicit without claiming live GPIO,
  `watchdog_set_drvdata()`, or watchdog-core side effects.
- matrix posture: this matrix records only those returned documentation surfaces
  and does not treat absent driver, test, survey, manifest, shared-contract, or
  build-route files as current-head evidence.

## Review Guardrails

- Treat this matrix as current direct-readback truthfulness only, not as proof
  of live platform behavior or hardware-backed validation.
- Keep teardown and failure-mode parity bounded to the returned module-slice and
  teardown-note checkpoint names until future rereads restore direct driver or
  replay surfaces.
- Do not use this note to claim live GPIO descriptor acquisition,
  `platform_set_drvdata()` execution, `watchdog_set_drvdata()` execution,
  `devm_watchdog_register_device()` execution, platform-driver registration,
  watchdog-core registration, remove hooks, reboot-backed teardown execution, or
  hardware-validated parity.
- If a future reread restores any gpio driver, replay, manifest, survey, or
  shared-route file, refresh this matrix together with the reopened companion
  surface in one bounded pass.

## Next Blocked Step

The next honest gpio-only follow-up is still one equally small same-lane
truthfulness repair or one directly returned replay or driver surface recovery
around teardown or failure-mode parity, rather than new runtime behavior.
