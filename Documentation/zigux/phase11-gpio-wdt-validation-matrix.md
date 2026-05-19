# Phase 11 GPIO Watchdog Validation Matrix

This document records the bounded gpio watchdog validation matrix for the current
Zigux Phase 11 simple-driver packet.

## Status

- `PHASE11_GPIO_WDT_STATUS=driver_and_docs_packet_truthful`
- lane: `P11-L04`
- reviewed against live `master`
- scope: keep the current gpio watchdog teardown and failure-mode packet honest
  without widening into live GPIO descriptor acquisition, platform-driver
  registration, watchdog-core registration, remove hooks, reboot-backed teardown
  execution, or hardware-backed validation

## Current Repo Reality

The directly readable gpio watchdog matrix packet on current `master` is:

- `drivers/watchdog/gpio_wdt.zig`
- `Documentation/zigux/phase11-gpio-wdt-survey.md`
- `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
- `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`

Current direct contents reads in this run do not rematerialize
`zigux/tests/phase11_gpio_wdt.zig`,
`zigux/tests/phase11_gpio_wdt_platform_drvdata.zig`,
`zigux/tests/phase11_gpio_wdt_manifest.json`,
`zigux/tests/phase11_gpio_wdt_survey.zig`,
`Documentation/zigux/phase11-shared-replay-contract.md`, or
`zigux/tests/phase11_build.zig`, so this matrix cannot present those deeper
replay and route surfaces as current direct-readback packet members.

## Current Direct-Readback Matrix

Treat the current gpio watchdog matrix packet as the driver-plus-docs packet
below:

- `drivers/watchdog/gpio_wdt.zig`
- `Documentation/zigux/phase11-gpio-wdt-survey.md`
- `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
- `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`

The returned driver plus the paired module slice and teardown note keep the
bounded `descriptorRequestSummary()`, `timeoutPropertyCheckpointSummary()`,
`platformDrvdataCheckpointSummary()`, `nowayoutPolicySummary()`,
`registrationHandoffSummary()`, `registrationPlanSummary()`,
`registerDeviceCallSummary()`, `registerDeviceFailureSummary()`, `requestStop()`,
and `summarizeTeardown()` checkpoint names reviewable as driver-backed teardown
and failure-mode surfaces.

## Teardown And Failure-Mode Review Surface

- driver anchor: `drivers/watchdog/gpio_wdt.zig` keeps the bounded descriptor,
  timeout-property, platform-drvdata ordering, nowayout policy, registration,
  register-device failure, and teardown checkpoint names directly readable
  without claiming live side effects.
- teardown handoff: `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
  keeps the bounded stop-request split, register-device failure cues, and
  teardown ownership explicit without claiming remove-hook or reboot-backed
  shutdown execution.
- failure-mode packet: `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
  keeps the bounded checkpoint names explicit without claiming live GPIO,
  `watchdog_set_drvdata()`, or watchdog-core side effects.
- matrix posture: this matrix records only those returned driver and
  documentation surfaces and does not treat absent replay, manifest, survey
  gate, shared-contract, or build-route files as current-head evidence.

## Review Guardrails

- Treat this matrix as current direct-readback truthfulness only, not as proof
  of live platform behavior or hardware-backed validation.
- Keep teardown and failure-mode parity bounded to the returned driver and
  directly coupled docs packet until future rereads restore focused replay or
  build-route surfaces.
- Do not use this note to claim live GPIO descriptor acquisition,
  `platform_set_drvdata()` execution, `watchdog_set_drvdata()` execution,
  `devm_watchdog_register_device()` execution, platform-driver registration,
  watchdog-core registration, remove hooks, reboot-backed teardown execution, or
  hardware-validated parity.
- If a future reread restores any gpio replay, manifest, survey gate, or shared-route
  file, refresh this matrix together with the reopened companion surface in one
  bounded pass.

## Next Blocked Step

The next honest gpio-only follow-up is still one equally small same-lane
truthfulness repair or one directly returned replay or route recovery around
teardown or failure-mode parity, rather than new runtime behavior.
