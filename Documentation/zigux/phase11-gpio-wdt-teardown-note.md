# Phase 11 GPIO Watchdog Teardown Note

This note restores the missing teardown-facing checkpoint for the bounded Phase 11 `gpio_wdt` packet on current `master`.
It stays inside the simple-drivers lane and records only the host-free teardown and stop-policy surfaces that the shipped GPIO survey packet already describes.

## Status

* `PHASE11_GPIO_WDT_TEARDOWN_STATUS=teardown_handoff_archived`
* teardown evidence remains bounded to the landed `gpio_wdt` starter packet
* remaining follow-through is still live GPIO descriptor lookup, platform-driver registration, watchdog-core registration, remove hooks, reboot-backed teardown execution, failure-mode parity beyond the landed bounded starter checks, and hardware-backed validation

## Teardown Packet

The current teardown-facing GPIO packet on `master` is:

* `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
* `Documentation/zigux/phase11-gpio-wdt-survey.md`
* `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
* `zigux/tests/phase11_gpio_wdt.zig`
* `zigux/tests/phase11_gpio_wdt_manifest.json`

These surfaces keep the teardown packet readable beside the shared Phase 11 replay route without promoting it into a broader runtime-parity claim.

## What The Landed Teardown Packet Covers

The current host-free teardown replay keeps these handoffs explicit:

* `teardownSummary()` and the bounded stop-request outcomes it records
* the split between watchdog-core stop policy and hardware `always-running` behavior
* the teardown handoff after descriptor preflight, timeout-property bookkeeping, `platform_set_drvdata()` ordering, `watchdog_set_drvdata()` ordering, and the first bounded register-device request surface
* `rebootGlueCheckpointSummary()` and the bounded `watchdog_stop_on_reboot()` ordering it records between `nowayout`, pre-registration start, and the later register-device request surface
* teardown-facing failure-mode cues that stay reviewable without claiming live remove-hook or reboot-backed shutdown execution

The landed survey-backed packet also keeps the stop-transition, reboot-glue checkpoint, teardown-ownership boundaries, and bounded failure-mode cues visible beside the starter replay without claiming live GPIO execution, platform cleanup callbacks, or host-backed shutdown behavior.

## Bounded Meaning

This note records the shipped teardown summaries only.
It does not claim live GPIO descriptor acquisition, `platform_set_drvdata()` execution, `watchdog_set_drvdata()` execution, `devm_watchdog_register_device()` execution, platform-driver registration, live reboot-hook registration, remove-hook parity, failure-mode parity beyond the landed bounded starter checks, or hardware-validated teardown parity.
Those remain later same-lane follow-through steps rather than part of the already-landed archival packet.
