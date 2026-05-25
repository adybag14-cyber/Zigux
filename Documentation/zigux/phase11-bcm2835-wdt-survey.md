# Phase 11 BCM2835 Watchdog Survey
This note keeps the current Phase 11 `bcm2835_wdt` lane truthful on `master`. It stays inside the watchdog family and records the bounded starter packet that is now directly readable on current `master`, without overclaiming live platform registration, hardware-backed poweroff execution, or wider reminder surfaces that have not returned yet.

## Status
* `PHASE11_BCM2835_WDT_SURVEY_STATUS=survey_gate_landed`
* roadmap phase: `Phase 11`
* archival packet identity remains `P11-L08`
* current scheduled continuity for this archival bcm2835 packet is tracked through `P11-L10`
* Linux anchor: `drivers/watchdog/bcm2835_wdt.c`
* current direct `master` readback now materializes `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, `Documentation/zigux/phase11-bcm2835-wdt-platform-validation-plan.md`, `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig`, `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig`, `drivers/watchdog/bcm2835_wdt.zig`, `drivers/watchdog/bcm2835_wdt_verify.zig`, and `zigux/tests/phase11_bcm2835_wdt.zig`
* direct current `master` readback still does not return `Documentation/zigux/phase11-bcm2835-wdt-slice.md`, `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`, or `zigux/tests/phase11_bcm2835_wdt_manifest.json`, so this survey keeps the packet narrowed to the live driver, verify-helper, validation-plan, validation-matrix, and focused replay surfaces only
* the Phase 11 simple-driver roadmap gap is closed at bounded current-driver depth on `master` because the live driver proof, coupled verify helper, validation plan, validation matrix, focused replay, and dedicated reminder-packet survey route are directly readable together
* remaining blocked work is still live platform registration, PM-base plumbing, watchdog-core registration, shared poweroff-handler installation, and hardware-backed validation beyond the current starter packet

## Current Repo Reality
Current `master` keeps this bounded bcm2835 packet reviewable through:
* the survey note in `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
* the explicit blocker boundary in `Documentation/zigux/phase11-bcm2835-wdt-platform-validation-plan.md`
* the current-head validation matrix in `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
* the focused reminder-packet replay in `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig`
* the dedicated replay route in `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig`
* the bounded driver-return proof in `drivers/watchdog/bcm2835_wdt.zig`
* the coupled verify-helper replay in `drivers/watchdog/bcm2835_wdt_verify.zig`
* the focused tests-root replay in `zigux/tests/phase11_bcm2835_wdt.zig`

The still-blocked wider reminder surfaces `Documentation/zigux/phase11-bcm2835-wdt-slice.md`, `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`, and `zigux/tests/phase11_bcm2835_wdt_manifest.json` remain out of the current-head packet until a later same-lane follow-through returns them with proof that matches the live driver, verify helper, and matrix boundary.

## Bounded Meaning
This survey note records a bounded Phase 11 closure at current-driver depth only. It does not claim live platform registration, PM-base execution, watchdog-core registration, shared poweroff-handler installation, hardware-backed poweroff execution, or that the wider slice, teardown-note, and manifest surfaces have already returned. It records one narrower fact: current `master` now carries the bcm2835 driver proof, verify helper, validation plan, validation matrix, focused replay, and reminder-packet survey surfaces needed to satisfy the roadmap's simple-driver expectation for this lane, while wider platform behavior and wider reminder surfaces remain intentionally blocked.

## Next Bounded Step
The next honest same-lane follow-through is one explicit manifest-backed closure, slice-note, or teardown-note return that matches the live driver, verify helper, and validation matrix first and only then widens into broader platform behavior.