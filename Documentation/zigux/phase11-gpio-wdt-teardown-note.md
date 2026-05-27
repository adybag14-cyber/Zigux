# Phase 11 GPIO Watchdog Teardown Note

This note keeps the teardown-facing checkpoint for the bounded Phase 11
`gpio_wdt` packet truthful on current `master`. It stays inside the
simple-drivers lane and records the returned driver-plus-docs-plus-proof
surfaces that already describe the host-free teardown and stop-policy packet.

## Status

- `PHASE11_GPIO_WDT_TEARDOWN_STATUS=teardown_handoff_driver_docs_and_proof_packet`
- teardown evidence remains bounded to the returned gpio driver, direct proofs,
  current-head manifest, dedicated replay routes, and coupled docs packet
- remaining follow-through is still wider focused replay or manifest recovery,
  live GPIO descriptor lookup, platform-driver registration, watchdog-core
  registration, live platform cleanup callbacks, reboot-backed teardown
  execution, and hardware-backed validation

## Teardown Packet

The current teardown-facing GPIO packet on `master` is:

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
- `zigux/tests/phase11_gpio_wdt_current_head_manifest.json`
- `zigux/tests/phase11_gpio_wdt_current_head_manifest_survey.zig`
- `zigux/tests/phase11_gpio_wdt_current_head_manifest_survey_build.zig`
- `Documentation/zigux/phase11-gpio-wdt-survey.md`
- `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
- `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
- `Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`

These returned driver, driver-backed verify helper, direct proofs, current-head
manifest, dedicated replay routes, and documentation surfaces keep the teardown
packet readable without promoting absent wider replay, survey, manifest, or
shared-build files into current-head evidence.

## What The Landed Teardown Packet Covers

The current host-free teardown review packet keeps these handoffs explicit:

- `summarizeTeardown()` and the bounded stop-request outcomes it records
- `requestStop()` and the split between watchdog-core stop policy and hardware
  `always-running` behavior
- `drivers/watchdog/gpio_wdt_verify.zig` as the driver-backed verify helper
  that keeps `registrationPlanSummary()`, `registerDeviceCallSummary()`,
  `registerDeviceFailureSummary()`, `rebootGlueCheckpointSummary()`,
  `summarizeTeardown()`, and `summarizeRemoveHandoff()` replayable beside the
  direct proofs without claiming live GPIO, live watchdog-core registration,
  live remove-hook execution, or reboot-backed shutdown execution
- `zigux/tests/phase11_gpio_wdt_verify_helper_build.zig` as the dedicated
  bounded replay route that keeps the driver-backed verify helper on its own
  `zig build` path instead of leaving teardown-helper validation implicit
- `zigux/tests/phase11_gpio_wdt_preflight_review.zig` as the direct preflight
  proof surface that keeps `descriptorPreflightSummary()`,
  `timeoutPropertyCheckpointSummary()`, `platformDrvdataCheckpointSummary()`,
  and `watchdogDrvdataCheckpointSummary()` explicit before reboot glue or
  register-device execution claims
- `nowayoutPolicySummary()` as a directly replayed checkpoint through
  `zigux/tests/phase11_gpio_wdt_nowayout_policy_review.zig`, keeping the
  bounded stopped, blocked-by-nowayout, and kept-running split explicit without
  needing a wider shared replay packet
- `registerDeviceFailureSummary()` and the teardown-facing failure-mode cues
  that stay reviewable without claiming live remove-hook or reboot-backed
  shutdown execution
- `zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig` as the direct
  proof surface that keeps the first bounded register-device request, the paired
  failure summary, and the teardown-facing stop-policy split tied to the
  reboot-glue boundary without claiming live watchdog-core registration
- `zigux/tests/phase11_gpio_wdt_remove_handoff_review.zig` as the direct proof
  surface that keeps `platformCleanupCheckpointSummary()` and
  `summarizeRemoveHandoff()` replayable as the cleanup-to-remove handoff packet
  without claiming live platform cleanup callbacks, platform-driver removal,
  watchdog-core unregister side effects, or host-backed shutdown execution
- `zigux/tests/phase11_gpio_wdt_current_head_manifest.json` as the machine-
  readable inventory that keeps the returned teardown packet explicit without
  overclaiming that the older wider gpio manifest or shared build route has
  returned
- `zigux/tests/phase11_gpio_wdt_current_head_manifest_survey.zig` and
  `zigux/tests/phase11_gpio_wdt_current_head_manifest_survey_build.zig` as the
  dedicated fail-closed route that rechecks the recovered manifest, coupled
  survey note, teardown note, remove-handoff note, module slice, and validation
  matrix packet
- `zigux/tests/phase11_gpio_wdt_preflight_review_build.zig`,
  `zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig`,
  `zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig`,
  `zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig`, and
  `zigux/tests/phase11_gpio_wdt_verify_helper_build.zig` as the dedicated
  bounded replay routes for the returned teardown packet
- `timeoutPropertyCheckpointSummary()` and
  `platformDrvdataCheckpointSummary()` as the ordering anchors that still feed
  the bounded register-device and teardown summaries
- `watchdogDrvdataCheckpointSummary()` and `rebootGlueCheckpointSummary()` as
  the bounded ownership-to-reboot-glue handoff before the first
  `watchdog_stop_on_reboot()` request surface
- `platformCleanupCheckpointSummary()` as the bounded cleanup-ordering bridge
  between teardown and remove handoff before any live platform cleanup
  callback, platform-driver removal, watchdog-core unregister side effects, or
  host-backed shutdown execution claim
- `Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md` as the
  companion surface that keeps the bounded remove-handoff packet explicit
  without claiming live platform cleanup callbacks, platform-driver removal,
  watchdog-core unregister side effects, or host-backed shutdown execution
- `python3 scripts/zigux/check-phase11-gpio-current-head-manifest.py --self-test`
  and `python3 scripts/zigux/check-phase11-gpio-current-head-manifest.py` as
  the direct truthfulness guard for the recovered current-head manifest packet
- the teardown handoff after descriptor preflight and the first bounded
  register-device request surface

The returned driver-backed packet and verify helper also keep the
stop-transition, direct nowayout-policy proof, reboot-glue handoff,
platform-cleanup checkpoint, remove-handoff boundary, and teardown-ownership
boundaries visible without claiming live `watchdog_set_drvdata()` execution,
live `watchdog_stop_on_reboot()` execution, live GPIO execution, live platform
cleanup callbacks, or host-backed shutdown behavior.

## Bounded Meaning

This note records the returned teardown summaries, direct proofs, current-head
manifest evidence, and dedicated replay routes only. It does not claim live
GPIO descriptor acquisition, `platform_set_drvdata()` execution,
`watchdog_set_drvdata()` execution, `watchdog_stop_on_reboot()` execution,
`devm_watchdog_register_device()` execution, platform-driver registration, live
reboot-hook registration, live platform cleanup callbacks, live remove-hook
execution, or hardware-validated teardown parity. Those remain later same-lane
follow-through steps rather than part of the already-landed packet.
