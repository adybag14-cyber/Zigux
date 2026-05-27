# Phase 11 GPIO Watchdog Module Slice

This bounded Phase 11 `P11-L04` gpio watchdog review packet keeps the current
driver-plus-docs-plus-proof packet truthful on current `master`.
It records the returned driver, direct proofs, current-head manifest, dedicated
manifest survey route, and coupled note surfaces that authenticated contents
reads still rematerialize and does not treat older wider replay, manifest,
survey-gate, shared-contract, or shared-build anchors as current-head evidence.

## Review Packet

The `gpio_wdt_lab` starter remains intentionally review-first while still
exposing the shipped checkpoint names that the returned driver, proof, current-
head manifest, and companion notes keep explicit:
- `platformDriverIdentitySummary()` keeps the Linux anchor and bounded starter
  identity explicit.
- `watchdogMetadataSummary()` keeps the watchdog metadata packet visible before
  later live registration work.
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
- `zigux/tests/phase11_gpio_wdt_current_head_manifest.json` keeps the returned
  driver-plus-docs-plus-proof packet machine-readable without reviving the
  older wider manifest or shared replay route.
- `zigux/tests/phase11_gpio_wdt_current_head_manifest_survey.zig` and
  `zigux/tests/phase11_gpio_wdt_current_head_manifest_survey_build.zig` keep
  the narrower current-head packet on a dedicated fail-closed survey route.

The same review packet also keeps teardown and failure-mode parity explicit in
bounded form while the paired
`Documentation/zigux/phase11-gpio-wdt-teardown-note.md` and
`Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md` keep the current
teardown and remove-handoff packet explicit without claiming live platform
cleanup callbacks, platform-driver removal, watchdog-core unregister side
effects, or host-backed shutdown behavior.

`python3 scripts/zigux/check-phase11-gpio-current-head-manifest.py --self-test`
and `python3 scripts/zigux/check-phase11-gpio-current-head-manifest.py` keep
the recovered manifest, survey note, module slice, teardown note,
remove-handoff note, validation matrix, and dedicated survey build route
aligned on current `master`.

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
