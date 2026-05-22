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
- `zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig`
- `Documentation/zigux/phase11-gpio-wdt-survey.md`
- `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
- `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
- `Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`

Current direct contents reads in this run do not rematerialize the older wider
replay and route surfaces `zigux/tests/phase11_gpio_wdt.zig`,
`zigux/tests/phase11_gpio_wdt_manifest.json`, or `zigux/tests/phase11_build.zig`,
so keep the remove-handoff packet bounded to the returned driver, proof, and
coupled docs surfaces instead of treating absent wider replay, manifest, or
shared-build files as current-head evidence.

## Returned Remove-Handoff Surface

- `registerDeviceFailureSummary()` keeps register-device failure cues reviewable
  before any later remove-hook execution claim.
- `zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig` keeps the
  register-device failure summary and first bounded register-device request tied
  to the reboot-glue boundary before any later remove-hook execution claim.
- `requestStop()` keeps the bounded nowayout, stopped, and kept-running stop
  split explicit before any platform cleanup callback claim.
- `rebootGlueCheckpointSummary()` keeps the stop-on-reboot handoff visible
  before any later remove-hook execution claim.
- `summarizeTeardown()` keeps the stop-request, register-device-failure, and
  reboot-glue checkpoint cues reviewable as the teardown input to the bounded
  remove-handoff packet.
- `summarizeRemoveHandoff()` keeps the dedicated remove-handoff summary itself
  explicit before any live platform cleanup callback, platform-driver removal,
  watchdog-core unregister, or host-backed shutdown claim.

## Guardrails

This note does not claim live platform cleanup callbacks, platform-driver
removal, watchdog-core unregister side effects, reboot-backed teardown
execution, or hardware-backed validation.

## Next Blocked Step

The next honest gpio-only follow-through remains wider focused replay or
manifest recovery, or another equally small gpio watchdog truthfulness repair,
rather than new runtime behavior.
