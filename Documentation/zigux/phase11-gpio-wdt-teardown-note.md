# Phase 11 GPIO Watchdog Teardown Note

This note keeps the archived teardown-facing checkpoint for the bounded Phase 11 `gpio_wdt` packet truthful on current `master`.
It stays inside the simple-drivers lane and records only the host-free teardown and stop-policy surfaces that the visible starter and the still-visible review packet can support today.

## Status

* `PHASE11_GPIO_WDT_TEARDOWN_STATUS=visible_starter_teardown_review_surface`
* teardown evidence remains bounded to the visible starter plus the archived `gpio_wdt` review packet on current `master`
* remaining follow-through is still restoring the directly coupled main replay and shared build route, plus later live GPIO descriptor lookup, platform-driver registration, watchdog-core registration, remove hooks, reboot-backed teardown execution, failure-mode parity beyond the current bounded packet, and hardware-backed validation

## Teardown Packet

The current teardown-facing GPIO review packet still directly visible on `master` is:

* `drivers/watchdog/gpio_wdt.zig`
* `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
* `Documentation/zigux/phase11-gpio-wdt-survey.md`
* `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
* `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
* `zigux/tests/phase11_gpio_wdt_manifest.json`
* `zigux/tests/phase11_gpio_wdt_survey.zig`
* `zigux/tests/phase11_gpio_wdt_platform_drvdata.zig`

Direct current-`master` contents reads still do not expose `zigux/tests/phase11_gpio_wdt.zig` or `zigux/tests/phase11_build.zig`.

These surfaces keep the bounded teardown packet readable without promoting it into a broader runtime-parity claim or treating the older shared replay route as current shipped evidence.

## What The Visible Teardown Packet Covers

The current visible starter and archived gpio watchdog review packet keep these teardown-facing handoffs explicit:

* `summarizeTeardown()` and the bounded stop-request outcomes recorded through `requestStop()`
* the split between watchdog-core stop policy and hardware `always-running` behavior through `nowayoutPolicySummary()`
* the teardown handoff after descriptor request summary, `platform_set_drvdata()` ordering, `watchdogDrvdataCheckpointSummary()`, probe-time bookkeeping, registration handoff, and the first bounded register-device request surface
* teardown-facing failure-mode cues that stay reviewable through `registerDeviceFailureSummary()` without claiming live remove-hook or reboot-backed shutdown execution

The still-visible focused `platform_set_drvdata()` replay keeps one early ordering checkpoint directly replayable on current `master`, while the dedicated survey gate keeps the surrounding stop-transition, teardown-ownership boundaries, and bounded failure-mode cues freshly checked as archived review memory only.

## Bounded Meaning

This note records bounded teardown summaries only.
It does not claim the missing main replay on current `master`, the missing shared Phase 11 build route, live GPIO descriptor acquisition, `platform_set_drvdata()` execution, `watchdog_set_drvdata()` execution, `devm_watchdog_register_device()` execution, platform-driver registration, live reboot-hook registration, remove-hook parity, failure-mode parity beyond the current bounded review packet, or hardware-validated teardown parity.
Those remain later same-lane follow-through steps rather than part of the currently visible packet.
