# Phase 11 BCM2835 Watchdog Survey
This note keeps the current Phase 11 `bcm2835_wdt` lane truthful on `master`. It stays inside the watchdog family and records the surviving reminder packet together with one new driver-backed verify helper, the existing driver-return proof boundary, and one matching validation matrix without overclaiming a full starter packet, live platform registration, or hardware-backed poweroff execution.

## Status
* `PHASE11_BCM2835_WDT_SURVEY_STATUS=survey_gate_landed`
* roadmap phase: `Phase 11`
* archival packet identity remains `P11-L08`
* Linux anchor: `drivers/watchdog/bcm2835_wdt.c`
* current direct `master` readback now materializes `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, `Documentation/zigux/phase11-bcm2835-wdt-platform-validation-plan.md`, `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig`, `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig`, `drivers/watchdog/bcm2835_wdt.zig`, `drivers/watchdog/bcm2835_wdt_verify.zig`, and `zigux/tests/phase11_bcm2835_wdt.zig`
* current direct `master` readback does not return `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `Documentation/zigux/phase11-bcm2835-wdt-slice.md`, or `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`
* the Phase 11 simple-driver roadmap gap is no longer reminder-only on current `master`; the surviving bcm2835 packet now includes one bounded driver-return proof plus a coupled verify helper and a validation matrix for timeout bounds, restart constants, PM-base handoff gating, and poweroff-ownership summaries
* remaining blocked work is still manifest or slice or teardown-note follow-through, live platform registration, PM-base plumbing, watchdog-core registration, shared poweroff-handler installation, and hardware-backed validation beyond the current reminder-plus-driver-plus-verify packet

## Current Repo Reality
Current `master` keeps this bounded bcm2835 packet reviewable through:
* the survey note in `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
* the explicit blocker boundary in `Documentation/zigux/phase11-bcm2835-wdt-platform-validation-plan.md`
* the current-head validation matrix in `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
* the focused reminder-packet replay in `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig`
* the dedicated replay route in `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig`
* the minimal driver-return proof in `drivers/watchdog/bcm2835_wdt.zig`
* the coupled verify-helper replay in `drivers/watchdog/bcm2835_wdt_verify.zig`
* the focused tests-root replay in `zigux/tests/phase11_bcm2835_wdt.zig`

## Bounded Meaning
This survey note does not claim a manifest-backed closure packet, slice note, teardown note, live platform registration, PM-base execution, watchdog-core registration, or hardware-backed poweroff execution. It records one narrower fact: current `master` now has a small bcm2835 driver-return proof, a coupled verify helper, and a matching validation matrix for the timeout window, restart constants, blocked PM-base handoff states, and poweroff ownership outcomes, while the wider Phase 11 starter packet remains incomplete.

## Next Bounded Step
The next honest same-lane follow-through is one bcm2835-only manifest-backed closure or teardown-note step that matches this reminder-plus-driver-plus-verify-plus-matrix packet without widening into `gpio_wdt`, `dw_wdt`, shared Phase 11 wording, or speculative hardware claims.
