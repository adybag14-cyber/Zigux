# Phase 11 GPIO Watchdog Teardown Note

This note keeps the archived teardown-facing checkpoint for the bounded Phase 11 `gpio_wdt` packet truthful on current `master`.
It stays inside the simple-drivers lane and records only the host-free teardown and stop-policy surfaces that the still-visible gpio watchdog review packet can support today.

## Status

* `PHASE11_GPIO_WDT_TEARDOWN_STATUS=teardown_handoff_archived`
* teardown evidence remains bounded to the archived `gpio_wdt` review packet on current `master`
* remaining follow-through is still restoring the visible main driver packet, plus live GPIO descriptor lookup, platform-driver registration, watchdog-core registration, remove hooks, reboot-backed teardown execution, failure-mode parity beyond the archived bounded review packet, and hardware-backed validation

## Teardown Packet

The current teardown-facing GPIO review packet still directly visible on `master` is:

* `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
* `Documentation/zigux/phase11-gpio-wdt-survey.md`
* `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
* `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
* `zigux/tests/phase11_gpio_wdt_manifest.json`
* `zigux/tests/phase11_gpio_wdt_survey.zig`
* `zigux/tests/phase11_gpio_wdt_platform_drvdata.zig`

Direct current-`master` contents reads still do not expose `drivers/watchdog/gpio_wdt.zig`, `zigux/tests/phase11_gpio_wdt.zig`, or `zigux/tests/phase11_build.zig`.

These surfaces keep the archived teardown packet readable without promoting it into a broader runtime-parity claim or treating the older shared replay route as current shipped evidence.

## What The Archived Teardown Packet Covers

The current archived gpio watchdog review packet still keeps these teardown-facing handoffs explicit:

* `teardownSummary()` and the bounded stop-request outcomes it records
* the split between watchdog-core stop policy and hardware `always-running` behavior
* the teardown handoff after descriptor preflight, timeout-property bookkeeping, `platform_set_drvdata()` ordering, `watchdog_set_drvdata()` ordering, and the first bounded register-device request surface
* `rebootGlueCheckpointSummary()` and the bounded `watchdog_stop_on_reboot()` ordering it records between `nowayout`, pre-registration start, and the later register-device request surface
* teardown-facing failure-mode cues that stay reviewable without claiming live remove-hook or reboot-backed shutdown execution

The still-visible focused `platform_set_drvdata()` replay keeps one early ordering checkpoint directly replayable on current `master`, while the restored dedicated survey gate keeps the surrounding stop-transition, reboot-glue checkpoint, teardown-ownership boundaries, and bounded failure-mode cues freshly checked as archived review memory only.

## Bounded Meaning

This note records archived teardown summaries only.
It does not claim visible main-driver scaffolding on current `master`, live GPIO descriptor acquisition, `platform_set_drvdata()` execution, `watchdog_set_drvdata()` execution, `devm_watchdog_register_device()` execution, platform-driver registration, live reboot-hook registration, remove-hook parity, failure-mode parity beyond the archived bounded review packet, or hardware-validated teardown parity.
Those remain later same-lane follow-through steps rather than part of the currently visible archived packet.
