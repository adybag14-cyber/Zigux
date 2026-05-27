# Phase 11 BCM2835 Watchdog Survey
This note keeps the current Phase 11 `bcm2835_wdt` lane truthful on `master`. It stays inside the watchdog family and records the bounded starter packet that is now directly readable on current `master`, including the returned teardown note and machine-readable manifest packet, without overclaiming live platform registration, hardware-backed poweroff execution, or the wider slice surface that has not returned yet.

## Status
* `PHASE11_BCM2835_WDT_SURVEY_STATUS=survey_gate_landed`
* roadmap phase: `Phase 11`
* archival packet identity remains `P11-L08`
* current scheduled continuity for this archival bcm2835 packet is tracked through `P11-L10`
* Linux anchor: `drivers/watchdog/bcm2835_wdt.c`
* current direct `master` readback now materializes `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, `Documentation/zigux/phase11-bcm2835-wdt-platform-validation-plan.md`, `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`, `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig`, `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `drivers/watchdog/bcm2835_wdt.zig`, `drivers/watchdog/bcm2835_wdt_verify.zig`, and `zigux/tests/phase11_bcm2835_wdt.zig`
* direct current `master` readback still does not return `Documentation/zigux/phase11-bcm2835-wdt-slice.md`, so this survey keeps the packet narrowed to the live driver, verify-helper, manifest, teardown note, validation-plan, validation-matrix, and focused replay surfaces only
* the Phase 11 simple-driver roadmap gap is closed at bounded current-driver depth on `master` because the live driver proof, coupled verify helper, manifest-backed closure, teardown note, validation plan, validation matrix, focused replay, and dedicated reminder-packet survey route are directly readable together
* remaining blocked work is still live platform registration, PM-base plumbing, watchdog-core registration, shared poweroff-handler installation, remove-time callback release, and hardware-backed validation beyond the current starter packet

## Current Repo Reality
Current `master` keeps this bounded bcm2835 packet reviewable through:
* the survey note in `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
* the explicit blocker boundary in `Documentation/zigux/phase11-bcm2835-wdt-platform-validation-plan.md`
* the teardown-facing reminder note in `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`
* the current-head validation matrix in `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
* the focused reminder-packet replay in `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig`
* the dedicated replay route in `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig`
* the machine-readable manifest packet in `zigux/tests/phase11_bcm2835_wdt_manifest.json`
* the bounded driver-return proof in `drivers/watchdog/bcm2835_wdt.zig`
* the coupled verify-helper replay in `drivers/watchdog/bcm2835_wdt_verify.zig`
* the focused tests-root replay in `zigux/tests/phase11_bcm2835_wdt.zig`

The still-blocked wider reminder surface `Documentation/zigux/phase11-bcm2835-wdt-slice.md` remains out of the current-head packet until a later same-lane follow-through returns it with proof that matches the live driver, verify helper, manifest, teardown note, and matrix boundary.

## Bounded Meaning
This survey note records a bounded Phase 11 closure at current-driver depth only. It does not claim live platform registration, PM-base execution, watchdog-core registration, shared poweroff-handler installation, remove-time callback release, hardware-backed poweroff execution, or that the wider slice surface has already returned. It records one narrower fact: current `master` now carries the bcm2835 driver proof, verify helper, manifest-backed closure, teardown note, validation plan, validation matrix, focused replay, and reminder-packet survey surfaces needed to satisfy the roadmap's simple-driver expectation for this lane, while wider platform behavior and the slice surface remain intentionally blocked.

## Next Bounded Step
The next honest same-lane follow-through is one platform-registration or callback-ownership proof step that matches the live driver, verify helper, manifest, teardown note, and validation matrix first and only then widens into broader platform behavior.
