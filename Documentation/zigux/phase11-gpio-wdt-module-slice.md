# Phase 11 GPIO Watchdog Module Slice

This bounded Phase 11 module slice keeps the archived `P11-L04` gpio watchdog
review packet truthful on current `master`.
It records the returned driver-plus-docs-plus-proof packet that current
authenticated contents reads still rematerialize and does not treat older wider
replay, manifest, survey-gate, shared-contract, or shared-build anchors as
current-head evidence.

## Review Packet

The `gpio_wdt_lab` starter remains intentionally review-first while still
exposing the shipped checkpoint names that the returned driver, proof, and
companion notes keep explicit:
- `platformDriverIdentitySummary()` keeps the Linux anchor and bounded starter
  identity explicit.
- `watchdogMetadataSummary()` keeps the watchdog metadata packet visible before
  later live registration work.
- `drivers/watchdog/gpio_wdt_verify.zig` keeps the driver-backed verify helper
  replayable beside the direct proofs so `registrationPlanSummary()`,
  `registerDeviceCallSummary()`, `registerDeviceFailureSummary()`,
  `rebootGlueCheckpointSummary()`, `summarizeTeardown()`, and
  `summarizeRemoveHandoff()` stay directly reviewable without claiming live
  GPIO, watchdog-core registration, remove-hook execution, or reboot-backed
  shutdown behavior.
- `descriptorRequestSummary()` keeps the `devm_gpiod_get()` flag choice
  reviewable without claiming live descriptor acquisition.
- `descriptorPreflightSummary()` keeps the direct descriptor-preflight alias
  reviewable at the same bounded checkpoint before timeout parsing,
  drvdata-binding, reboot glue, or registration execution claims.
- `zigux/tests/phase11_gpio_wdt_preflight_review.zig` keeps
  `descriptorPreflightSummary()`, `timeoutPropertyCheckpointSummary()`,
  `platformDrvdataCheckpointSummary()`, and
  `watchdogDrvdataCheckpointSummary()` directly reviewable as one bounded
  preflight chain without claiming live GPIO acquisition, reboot glue
  execution, or watchdog-core registration.
- `timeoutPropertyCheckpointSummary()` keeps the timeout-property ordering
  reviewable before later live execution claims.
- `platformDrvdataCheckpointSummary()` keeps the early
  `platform_set_drvdata()` ordering explicit before later GPIO and watchdog
  bookkeeping.
- `watchdogDrvdataCheckpointSummary()` keeps the bounded
  `watchdog_set_drvdata()` ownership handoff explicit before later reboot glue
  or registration execution.
- `rebootGlueCheckpointSummary()` keeps the bounded
  `watchdog_stop_on_reboot()` handoff explicit between watchdog drvdata
  ownership and the first register-device request without claiming live shutdown
  execution.
- `nowayoutPolicySummary()` keeps the watchdog-core stop-policy split explicit
  before later reboot or teardown follow-through.
- `zigux/tests/phase11_gpio_wdt_nowayout_policy_review.zig` keeps
  `nowayoutPolicySummary()` directly reviewable across the bounded stopped,
  blocked-by-nowayout, and kept-running outcomes without claiming live
  watchdog-core registration or shutdown execution.
- `probeSummary()` keeps the probe-time bookkeeping visible without claiming
  live platform registration.
- `registrationIntentCheckpointSummary()` keeps timeout setup, nowayout
  application, stop-on-reboot ordering, and pre-registration start posture
  explicit before the first bounded register-device request.
- `zigux/tests/phase11_gpio_wdt_registration_intent_review.zig` keeps
  `registrationIntentCheckpointSummary()` and `registrationHandoffSummary()`
  directly reviewable as the registration-intent bridge before the first
  register-device request.
- `registrationHandoffSummary()` keeps the descriptor-facing and bookkeeping
  handoff reviewable before the first bounded register-device request.
- `registrationPlanSummary()` keeps the still-bounded watchdog registration
  plan explicit without claiming execution.
- `registerDeviceCallSummary()` keeps the first bounded
  `devm_watchdog_register_device()` request surface visible without claiming
  live watchdog-core registration.
- `registerDeviceFailureSummary()` keeps the bounded register-device failure
  cues explicit without promoting them into live watchdog-core behavior.
- `zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig` keeps the
  first bounded `devm_watchdog_register_device()` request surface and paired
  failure summary explicit beside the reboot-glue boundary without claiming live
  registration or shutdown execution.
- `summarizeTeardown()` keeps the host-free teardown summary visible without
  claiming reboot-backed shutdown execution.
- `platformCleanupCheckpointSummary()` keeps the cleanup-ordering bridge
  explicit between teardown and remove handoff before any live platform cleanup
  callback, platform-driver removal, or watchdog-core unregister claim.
- `zigux/tests/phase11_gpio_wdt_remove_handoff_review.zig` keeps
  `platformCleanupCheckpointSummary()` and `summarizeRemoveHandoff()`
  replayable as the cleanup-to-remove handoff packet without claiming live
  platform cleanup callbacks, platform-driver removal, watchdog-core unregister
  side effects, or host-backed shutdown execution.
- `zigux/tests/phase11_gpio_wdt_current_head_manifest.json` keeps the returned
  packet machine-readable without promoting the older wider manifest or shared
  replay routes into current-head evidence.
- `zigux/tests/phase11_gpio_wdt_current_head_manifest_survey.zig` and
  `zigux/tests/phase11_gpio_wdt_current_head_manifest_survey_build.zig` keep
  the module slice, survey note, validation matrix, and current-head manifest
  aligned through one dedicated bounded replay route.

The same review packet also keeps teardown and failure-mode parity explicit in
bounded form while the paired
`Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md` keeps the current
remove-handoff packet explicit without claiming live platform cleanup
callbacks, platform-driver removal, watchdog-core unregister side effects, or
host-backed shutdown behavior.

## Boundaries

This module slice does not promote absent wider replay, manifest, survey-gate,
shared-contract, or shared-build anchors into current-head evidence.

This module slice does not claim live GPIO descriptor acquisition, live
`watchdog_set_drvdata()` execution, live `watchdog_stop_on_reboot()` execution,
live `devm_watchdog_register_device()` execution, a live platform cleanup
callback, platform-driver removal, watchdog-core unregister side effects, a
host-backed shutdown callback, platform-driver registration, live reboot-hook
registration, or hardware-backed validation yet.

The next honest bounded step remains one equally small gpio watchdog replay,
manifest, checker, or validation-truthfulness repair inside this returned
driver-plus-docs-plus-proof packet, rather than new runtime behavior.
