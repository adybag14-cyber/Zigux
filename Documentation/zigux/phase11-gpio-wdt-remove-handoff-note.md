# Phase 11 GPIO Watchdog Remove Handoff Note

This note keeps the bounded gpio watchdog remove-handoff packet truthful on
current `master`.
It stays inside the simple-driver lane and records only the returned
driver-plus-docs-plus-proof surfaces that already keep teardown and
failure-mode parity reviewable without promoting live remove-hook execution.

## Status

- `PHASE11_GPIO_WDT_REMOVE_HANDOFF_STATUS=driver_docs_and_proof_remove_handoff_truthful`
- reviewed against live `master`
- scope: keep the bounded gpio watchdog remove-handoff packet truthful without
  widening into live platform cleanup callbacks, platform-driver removal,
  watchdog-core unregister side effects, reboot-backed teardown execution, or
  hardware-backed validation

## Current Repo Reality

The current remove-handoff-facing gpio packet on `master` is:

- `drivers/watchdog/gpio_wdt.zig`
- `drivers/watchdog/gpio_wdt_verify.zig`
- `zigux/tests/phase11_gpio_wdt_verify_helper_build.zig`
- `zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig`
- `zigux/tests/phase11_gpio_wdt_nowayout_policy_review.zig`
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

Current direct contents reads in this run do not rematerialize the older wider
replay and route surfaces `zigux/tests/phase11_gpio_wdt.zig`,
`zigux/tests/phase11_gpio_wdt_manifest.json`, or `zigux/tests/phase11_build.zig`,
so keep the remove-handoff packet bounded to the returned driver, proofs,
current-head manifest, and coupled docs surfaces instead of treating absent
wider replay, manifest, or shared-build files as current-head evidence.

## Returned Remove-Handoff Surface

- `registerDeviceFailureSummary()` keeps register-device failure cues reviewable
  before any later remove-hook execution claim.
- `zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig` keeps the
  register-device failure summary and first bounded register-device request tied
  to the reboot-glue boundary before any later remove-hook execution claim.
- `zigux/tests/phase11_gpio_wdt_nowayout_policy_review.zig` keeps
  `nowayoutPolicySummary()` explicit across the bounded stopped,
  blocked-by-nowayout, and kept-running split before any platform cleanup
  callback or remove-hook execution claim.
- `requestStop()` keeps the bounded nowayout, stopped, and kept-running stop
  split explicit before any platform cleanup callback claim.
- `rebootGlueCheckpointSummary()` keeps the stop-on-reboot handoff visible
  before any later remove-hook execution claim.
- `summarizeTeardown()` keeps the stop-request, register-device-failure, and
  reboot-glue checkpoint cues reviewable as the teardown input to the bounded
  remove-handoff packet.
- `platformCleanupCheckpointSummary()` keeps the bounded platform cleanup,
  driver-remove, and watchdog-unregister ordering explicit before any live
  platform cleanup callback, platform-driver removal, watchdog-core unregister,
  or host-backed shutdown claim.
- `zigux/tests/phase11_gpio_wdt_remove_handoff_review.zig` keeps
  `platformCleanupCheckpointSummary()` and `summarizeRemoveHandoff()` directly
  replayed as a dedicated cleanup-to-remove packet without claiming live
  platform cleanup callbacks, platform-driver removal, watchdog-core
  unregister, or host-backed shutdown execution.
- `zigux/tests/phase11_gpio_wdt_current_head_manifest.json` keeps the returned
  remove-handoff packet machine-readable without reviving the older wider gpio
  replay or manifest route.
- `zigux/tests/phase11_gpio_wdt_current_head_manifest_survey.zig` and
  `zigux/tests/phase11_gpio_wdt_current_head_manifest_survey_build.zig` keep
  the recovered manifest, survey note, module slice, teardown note,
  remove-handoff note, and validation matrix on one dedicated fail-closed route.
- `summarizeRemoveHandoff()` keeps the dedicated remove-handoff summary itself
  explicit before any live platform cleanup callback, platform-driver removal,
  watchdog-core unregister, or host-backed shutdown claim.
- `python3 scripts/zigux/check-phase11-gpio-current-head-manifest.py --self-test`
  and `python3 scripts/zigux/check-phase11-gpio-current-head-manifest.py` keep
  the current-head manifest packet aligned so this narrower remove-handoff
  evidence does not drift silently.

## Guardrails

This note does not claim live platform cleanup callbacks, platform-driver
removal, watchdog-core unregister side effects, reboot-backed teardown
execution, or hardware-backed validation.

## Next Blocked Step

The next honest gpio-only follow-through remains manifest recovery, checker
upkeep, or another equally small gpio watchdog truthfulness repair, rather than
new runtime behavior.
