# Phase 11 BCM2835 Watchdog Survey
This note keeps the current Phase 11 `bcm2835_wdt` lane truthful on `master`. It stays inside the watchdog family and records the surviving reminder packet plus the explicit blocker-plan boundary without overclaiming a current driver-backed starter, live platform registration, or hardware-backed poweroff execution.

## Status
* `PHASE11_BCM2835_WDT_SURVEY_STATUS=survey_gate_landed`
* roadmap phase: `Phase 11`
* archival packet identity remains `P11-L08`
* Linux anchor: `drivers/watchdog/bcm2835_wdt.c`
* current direct `master` readback now materializes `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, `Documentation/zigux/phase11-bcm2835-wdt-platform-validation-plan.md`, `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig`, and `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig`
* current direct `master` readback does not return `drivers/watchdog/bcm2835_wdt.zig`, `drivers/watchdog/bcm2835_wdt_verify.zig`, `zigux/tests/phase11_bcm2835_wdt.zig`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `Documentation/zigux/phase11-bcm2835-wdt-slice.md`, `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`, or `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
* the Phase 11 simple-driver roadmap gap is not closed at starter depth on current `master`; the surviving bcm2835 packet is a reminder surface plus an explicit validation-plan blocker for any future platform-facing return
* remaining blocked work is still a driver-backed starter return, live platform registration, PM-base plumbing, watchdog-core registration, shared poweroff-handler execution, and hardware-backed validation beyond the current reminder packet

## Current Repo Reality
Current `master` keeps this bounded bcm2835 packet reviewable through:
* the survey note in `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
* the explicit blocker boundary in `Documentation/zigux/phase11-bcm2835-wdt-platform-validation-plan.md`
* the focused reminder-packet replay in `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig`
* the dedicated replay route in `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig`

## Bounded Meaning
This survey note does not claim a live bcm2835 Zig driver, compile-local verify helper, direct replay helper, slice note, teardown note, validation matrix, platform registration, PM-base execution, watchdog-core registration, or hardware-backed poweroff execution. It records one narrower fact: the current bcm2835 packet on `master` is now a reminder surface plus an explicit blocker plan, and any future product progress in this family needs a fresh driver-backed return rather than more stale reminder-surface wording.

## Next Bounded Step
The next honest same-lane follow-through is one bcm2835-only platform-facing planning or driver-return step that can justify new current-head evidence without widening into `gpio_wdt`, `dw_wdt`, shared Phase 11 wording, or speculative hardware claims.