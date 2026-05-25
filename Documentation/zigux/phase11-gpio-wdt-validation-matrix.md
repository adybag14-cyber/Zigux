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
- `drivers/watchdog/gpio_wdt_verify.zig`
- `zigux/tests/phase11_gpio_wdt_verify_helper_build.zig`
- `zigux/tests/phase11_gpio_wdt_preflight_review.zig`
- `zigux/tests/phase11_gpio_wdt_preflight_review_build.zig`
- `zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig`
- `zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig`
- `zigux/tests/phase11_gpio_wdt_nowayout_policy_review.zig`
- `zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig`
- `zigux/tests/phase11_gpio_wdt_remove_handoff_review.zig`
- `zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig`
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
this matrix keeps the lane grounded on the returned driver, proofs, dedicated
bounded replay routes, and directly coupled docs surface only.

## Current Matrix

Treat the current gpio watchdog matrix packet as the driver-plus-docs-plus-proof
packet below:

- `drivers/watchdog/gpio_wdt.zig`
- `drivers/watchdog/gpio_wdt_verify.zig`
- `zigux/tests/phase11_gpio_wdt_verify_helper_build.zig`
- `zigux/tests/phase11_gpio_wdt_preflight_review.zig`
- `zigux/tests/phase11_gpio_wdt_preflight_review_build.zig`
- `zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig`
- `zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig`
- `zigux/tests/phase11_gpio_wdt_nowayout_policy_review.zig`
- `zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig`
- `zigux/tests/phase11_gpio_wdt_remove_handoff_review.zig`
- `zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig`
- `Documentation/zigux/phase11-gpio-wdt-survey.md`
- `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
- `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
- `Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`

The returned driver, the driver-backed verify helper, focused preflight proof,
focused register-device glue proof, focused nowayout policy proof, focused
remove-handoff proof, dedicated bounded replay routes, plus the paired module
slice, teardown note, and remove-handoff note keep the bounded
`platformDriverIdentitySummary()`, `watchdogMetadataSummary()`, `probeSummary()`,
`descriptorRequestSummary()`, `descriptorPreflightSummary()`,
`timeoutPropertyCheckpointSummary()`, `platformDrvdataCheckpointSummary()`,
`watchdogDrvdataCheckpointSummary()`,
`registrationIntentCheckpointSummary()`, `rebootGlueCheckpointSummary()`,
`registrationHandoffSummary()`, `registrationPlanSummary()`,
`registerDeviceCallSummary()`, `registerDeviceFailureSummary()`,
`nowayoutPolicySummary()`, `requestStop()`, `summarizeTeardown()`,
`platformCleanupCheckpointSummary()`, and `summarizeRemoveHandoff()` checkpoint
names directly reviewable as driver-backed teardown and failure-mode surfaces.

The direct preflight proof keeps `descriptorPreflightSummary()` matched to the
existing descriptor request packet while also machine-checking the timeout
property, `platform_set_drvdata()`, and `watchdog_set_drvdata()` ordering
through one bounded preflight route.

The driver-backed verify helper in `drivers/watchdog/gpio_wdt_verify.zig` keeps
`registrationPlanSummary()`, `registerDeviceCallSummary()`,
`registerDeviceFailureSummary()`, `rebootGlueCheckpointSummary()`,
`summarizeTeardown()`, and `summarizeRemoveHandoff()` compile-local and directly
replayed beside the dedicated focused proofs without claiming live GPIO,
platform-driver registration, watchdog-core registration, remove-hook
execution, or shutdown execution. The dedicated
`zigux/tests/phase11_gpio_wdt_verify_helper_build.zig` route keeps that helper
on its own bounded `zig build` path instead of leaving it implied by the wider
proof packet.

The direct nowayout proof keeps `nowayoutPolicySummary()` machine-checked
across the bounded stopped, blocked-by-nowayout, and kept-running outcomes,
while the existing register-device glue proof still carries the
registration-intent ordering and stop-policy split through
`registrationIntentCheckpointSummary()`, `requestStop()`, and
`summarizeTeardown()`.

The direct remove-handoff proof now machine-checks
`platformCleanupCheckpointSummary()` and `summarizeRemoveHandoff()` through a
dedicated bounded replay without claiming live platform cleanup callbacks,
platform-driver removal, watchdog-core unregister, or shutdown execution.

## Teardown And Failure-Mode Review Surface

- driver anchor: `drivers/watchdog/gpio_wdt.zig` keeps the bounded descriptor,
  timeout-property, platform-drvdata ordering, watchdog-drvdata ordering,
  reboot-glue handoff, nowayout policy, registration, register-device failure,
  teardown, and remove-handoff checkpoint names directly readable without
  claiming live side effects.
- direct verify-helper anchor: `drivers/watchdog/gpio_wdt_verify.zig` keeps the
  current registration-plan, register-device call, register-device failure,
  reboot-glue checkpoint, teardown, and remove-handoff summaries directly
  replayable as a driver-backed failure-mode packet without claiming live GPIO,
  watchdog-core registration, remove-hook execution, or shutdown execution.
- direct preflight proof anchor:
  `zigux/tests/phase11_gpio_wdt_preflight_review.zig` keeps the descriptor
  preflight alias, timeout-property ordering, and platform/watchdog drvdata
  ordering explicit before reboot glue or register-device execution claims.
- direct proof anchor: `zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig`
  keeps the first bounded `devm_watchdog_register_device()` request surface,
  the paired register-device failure summary, and the teardown-facing
  stop-policy split explicit without claiming live watchdog-core registration.
- direct nowayout proof anchor:
  `zigux/tests/phase11_gpio_wdt_nowayout_policy_review.zig` keeps
  `nowayoutPolicySummary()` explicit as a bounded stopped, blocked-by-nowayout,
  and kept-running packet without claiming live watchdog-core registration or
  reboot-backed teardown execution.
- direct remove-handoff proof anchor:
  `zigux/tests/phase11_gpio_wdt_remove_handoff_review.zig` keeps
  `platformCleanupCheckpointSummary()` and `summarizeRemoveHandoff()` explicit
  as a dedicated cleanup-to-remove packet without claiming live platform
  cleanup callbacks, platform-driver removal, watchdog-core unregister, or
  host-backed shutdown execution.
- dedicated replay routes:
  `zigux/tests/phase11_gpio_wdt_verify_helper_build.zig`,
  `zigux/tests/phase11_gpio_wdt_preflight_review_build.zig`,
  `zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig`,
  `zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig`, and
  `zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig` keep focused
  `zig build` validation paths available for the returned proof packet without
  pretending the older shared `phase11_build.zig` surface has returned.
- teardown handoff: `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
  keeps the bounded stop-request split, direct nowayout-policy proof,
  reboot-glue transition, and register-device failure cues explicit without
  claiming live remove-hook or reboot-backed shutdown execution.
- remove-handoff note: `Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`
  keeps the bounded remove-handoff packet explicit without claiming live
  platform cleanup callbacks, platform-driver removal, watchdog-core unregister,
  or host-backed shutdown execution.
- failure-mode packet: `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
  keeps the bounded checkpoint names explicit without claiming live GPIO,
  `watchdog_set_drvdata()` execution, `watchdog_stop_on_reboot()` execution, or
  watchdog-core side effects.
- matrix posture: this matrix records only the current driver, proofs,
  dedicated replay routes, and directly coupled documentation surfaces and does
  not treat absent wider replay, manifest, survey gate, shared-contract, or
  build-route files as current-head evidence.

## Review Guardrails

- Treat this matrix as current-head truthfulness only, not as proof of live
  platform behavior or hardware-backed validation.
- Keep teardown and failure-mode parity bounded to the current driver, the
  driver-backed verify helper, direct proofs, dedicated replay routes, and
  directly coupled docs packet until a later repo change restores wider replay
  or build-route surfaces.
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

The next honest gpio-only follow-up is still one equally small manifest,
checker, or validation-truthfulness repair, rather than new runtime behavior.
