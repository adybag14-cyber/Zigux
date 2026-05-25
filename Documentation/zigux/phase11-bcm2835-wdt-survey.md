# Phase 11 BCM2835 Watchdog Survey
This note keeps the current Phase 11 `bcm2835_wdt` lane truthful on `master`. It stays inside the watchdog family and records the bounded starter packet that is now directly readable on current `master`, without overclaiming live platform registration or hardware-backed poweroff execution.

## Status
* `PHASE11_BCM2835_WDT_SURVEY_STATUS=survey_gate_landed`
* roadmap phase: `Phase 11`
* archival packet identity remains `P11-L08`
* Linux anchor: `drivers/watchdog/bcm2835_wdt.c`
* current direct `master` readback now materializes `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, `Documentation/zigux/phase11-bcm2835-wdt-platform-validation-plan.md`, `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-bcm2835-wdt-slice.md`, `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`, `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig`, `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `drivers/watchdog/bcm2835_wdt.zig`, `drivers/watchdog/bcm2835_wdt_verify.zig`, and `zigux/tests/phase11_bcm2835_wdt.zig`
* the Phase 11 simple-driver roadmap gap is closed at starter depth on current `master` because the bounded driver template, validation matrix, teardown note, slice note, manifest, verify helper, and focused replay are all directly readable together
* remaining blocked work is still live platform registration, PM-base plumbing, watchdog-core registration, shared poweroff-handler installation, and hardware-backed validation beyond the current starter packet

## Current Repo Reality
Current `master` keeps this bounded bcm2835 packet reviewable through:
* the survey note in `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
* the explicit blocker boundary in `Documentation/zigux/phase11-bcm2835-wdt-platform-validation-plan.md`
* the current-head validation matrix in `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
* the bounded starter slice in `Documentation/zigux/phase11-bcm2835-wdt-slice.md`
* the remove-time and ownership reminder note in `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`
* the focused reminder-packet replay in `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig`
* the dedicated replay route in `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig`
* the manifest-backed packet record in `zigux/tests/phase11_bcm2835_wdt_manifest.json`
* the bounded driver-return proof in `drivers/watchdog/bcm2835_wdt.zig`
* the coupled verify-helper replay in `drivers/watchdog/bcm2835_wdt_verify.zig`
* the focused tests-root replay in `zigux/tests/phase11_bcm2835_wdt.zig`

## Bounded Meaning
This survey note records a bounded Phase 11 closure at starter depth only. It does not claim live platform registration, PM-base execution, watchdog-core registration, shared poweroff-handler installation, or hardware-backed poweroff execution. It records one narrower fact: current `master` now carries the bcm2835 starter packet surfaces needed to satisfy the roadmap's simple-driver expectation for this lane, while wider platform behavior remains intentionally blocked behind the explicit validation plan.

## Next Bounded Step
The next honest same-lane follow-through is not another reminder-only survey edit. Any future bcm2835 follow-through should be one driver-local or validation-plan step that justifies wider platform-registration or PM-base behavior without widening into `gpio_wdt`, `dw_wdt`, shared Phase 11 wording, or speculative hardware claims.
