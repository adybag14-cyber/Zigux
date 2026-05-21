# Phase 11 GPIO Watchdog Validation Matrix

This document records the bounded gpio watchdog validation matrix for the current
Zigux Phase 11 simple-driver packet.

## Status

- `PHASE11_GPIO_WDT_STATUS=driver_docs_and_proof_packet_truthful`
- lane: `P11-L04`
- reviewed against live `master`
- scope: keep the current gpio watchdog teardown and failure-mode packet honest
  without widening into live GPIO descriptor acquisition, platform-driver
  registration, watchdog-core registration, remove hooks, reboot-backed teardown
  execution, or hardware-backed validation

## Current Repo Reality

The current gpio watchdog matrix packet on `master` is:

- `drivers/watchdog/gpio_wdt.zig`
- `zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig`
- `Documentation/zigux/phase11-gpio-wdt-survey.md`
- `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
- `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
- `Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`

The older wider replay and route surfaces
`zigux/tests/phase11_gpio_wdt.zig`,
`zigux/tests/phase11_gpio_wdt_platform_drvdata.zig`,
`zigux/tests/phase11_gpio_wdt_manifest.json`,
`zigux/tests/phase11_gpio_wdt_survey.zig`,
`Documentation/zigux/phase11-shared-replay-contract.md`, and
`zigux/tests/phase11_build.zig` are not part of the current `master` packet, so
this matrix keeps the lane grounded on the returned driver, proof, and directly
coupled docs surface only.

## Current Matrix

Treat the current gpio watchdog matrix packet as the driver-plus-docs-plus-proof
packet below:

- `drivers/watchdog/gpio_wdt.zig`
- `zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig`
- `Documentation/zigux/phase11-gpio-wdt-survey.md`
- `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
- `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
- `Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`

The returned driver, focused register-device glue proof, plus the paired module
slice, teardown note, and remove-handoff note keep the bounded
`platformDriverIdentitySummary()`, `watchdogMetadataSummary()`,
`probeSummary()`, `descriptorRequestSummary()`,
`timeoutPropertyCheckpointSummary()`,
`platformDrvdataCheckpointSummary()`,
`watchdogDrvdataCheckpointSummary()`, `rebootGlueCheckpointSummary()`,
`registrationHandoffSummary()`, `registrationPlanSummary()`,
`registerDeviceCallSummary()`, `registerDeviceFailureSummary()`,
`requestStop()`, and `summarizeTeardown()` checkpoint names directly reviewable
as driver-backed teardown and failure-mode surfaces.

`nowayoutPolicySummary()` remains a current-head driver-local checkpoint that
this packet can cite, but the focused proof currently exercises the same
stop-policy split through `requestStop()` and `summarizeTeardown()` rather than
through a standalone nowayout-only replay.

## Teardown And Failure-Mode Review Surface

- driver anchor: `drivers/watchdog/gpio_wdt.zig` keeps the bounded descriptor,
  timeout-property, platform-drvdata ordering, watchdog-drvdata ordering,
  reboot-glue handoff, nowayout policy, registration, register-device failure,
  and teardown checkpoint names directly readable without claiming live side
  effects.
- direct proof anchor: `zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig`
  keeps the first bounded `devm_watchdog_register_device()` request surface,
  the paired register-device failure summary, and the teardown-facing
  stop-policy split explicit without claiming live watchdog-core registration.
- nowayout evidence boundary: treat `nowayoutPolicySummary()` as driver-local
  evidence for the current packet and treat `requestStop()` plus
  `summarizeTeardown()` as the direct proof route for the bounded nowayout,
  stopped, and kept-running split until a future gpio-only replay lands.
- teardown handoff: `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
  keeps the bounded stop-request split, reboot-glue transition, and
  register-device failure cues explicit without claiming live remove-hook or
  reboot-backed shutdown execution.
- remove-handoff note: `Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`
  keeps the bounded remove-handoff packet explicit without claiming live
  platform cleanup callbacks, platform-driver removal, watchdog-core unregister,
  or host-backed shutdown execution.
- failure-mode packet: `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
  keeps the bounded checkpoint names explicit without claiming live GPIO,
  `watchdog_set_drvdata()` execution, `watchdog_stop_on_reboot()` execution, or
  watchdog-core side effects.
- matrix posture: this matrix records only the current driver, proof, and
  directly coupled documentation surfaces and does not treat absent wider
  replay, manifest, survey gate, shared-contract, or build-route files as
  current-head evidence.

## Review Guardrails

- Treat this matrix as current-head truthfulness only, not as proof of live
  platform behavior or hardware-backed validation.
- Keep teardown and failure-mode parity bounded to the current driver, direct
  proof, and directly coupled docs packet until a later repo change restores
  wider replay or build-route surfaces.
- Do not describe the current packet as having a standalone nowayout-only replay
  route. The current direct proof keeps that stop-policy split reviewable
  through `requestStop()` and `summarizeTeardown()`.
- Do not use this note to claim live GPIO descriptor acquisition,
  `platform_set_drvdata()` execution, `watchdog_set_drvdata()` execution,
  `watchdog_stop_on_reboot()` execution,
  `devm_watchdog_register_device()` execution, platform-driver registration,
  watchdog-core registration, live platform cleanup callbacks, live remove-hook
  execution, reboot-backed teardown execution, or hardware-validated parity.
- If a future repo change restores any wider gpio replay, manifest, survey gate,
  or shared-route file, refresh this matrix together with the reopened
  companion surface in one bounded pass.

## Next Blocked Step

The next honest gpio-only follow-up is still one equally small replay,
manifest, checker, or validation-truthfulness repair, rather than new runtime
behavior.