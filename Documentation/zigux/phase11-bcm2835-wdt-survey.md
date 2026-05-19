# Phase 11 BCM2835 Watchdog Survey
This note keeps the current Phase 11 `bcm2835_wdt` lane truthful on `master`. It stays inside the watchdog family and records the directly reviewable starter packet plus the dedicated replay, verify, and survey surfaces without overclaiming live platform registration or hardware-backed poweroff execution.

## Status
* `PHASE11_BCM2835_WDT_SURVEY_STATUS=survey_gate_landed`
* roadmap phase: `Phase 11`
* archival packet identity remains `P11-L08`
* Linux anchor: `drivers/watchdog/bcm2835_wdt.c`
* current direct `master` readback now materializes the bounded bcm2835 starter, `drivers/watchdog/bcm2835_wdt_verify.zig`, `zigux/tests/phase11_bcm2835_wdt.zig`, `zigux/tests/phase11_bcm2835_wdt_survey.zig`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `Documentation/zigux/phase11-bcm2835-wdt-slice.md`, `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`, and `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
* the Phase 11 simple-driver roadmap gap is closed at starter depth because the lane now has a directly readable driver template, a hardware-validation matrix, teardown and failure-mode reminder surfaces, a manifest-backed packet note, and dedicated replay plus survey coverage
* remaining blocked work is still live platform registration, PM-base plumbing, watchdog-core registration, shared poweroff-handler execution, and hardware-backed validation beyond the current helper-backed packet

## Current Repo Reality
Current `master` keeps this bounded starter packet reviewable through:
* heartbeat bounds and watchdog-tick conversions in the driver helpers
* probe-state and platform-handoff summaries, including ownership cues for poweroff handling
* bounded runtime register-image modeling for `start()`, `stop()`, `restart()`, `poweroff()`, and `remove()`
* dedicated replay coverage in `zigux/tests/phase11_bcm2835_wdt.zig`
* compile-local verify coverage in `drivers/watchdog/bcm2835_wdt_verify.zig`
* dedicated survey-gate coverage in `zigux/tests/phase11_bcm2835_wdt_survey.zig`
* manifest-backed packet traceability in `zigux/tests/phase11_bcm2835_wdt_manifest.json` and `Documentation/zigux/phase11-bcm2835-wdt-slice.md`

## Bounded Meaning
This survey note does not claim live platform registration, PM-base execution, watchdog-core registration, or hardware-backed poweroff execution. It records one narrower fact: the bcm2835 watchdog starter now closes the roadmap gap at starter depth on current `master`, and the older target of "one bcm2835-only manifest or slice-note extension" is already satisfied by the landed manifest and slice note.

## Next Bounded Step
The next honest same-lane follow-through is no longer another reminder-surface add. Keep future bcm2835 work inside a later driver-local or explicit validation-plan step that can justify any wider platform-registration or PM-base behavior without widening into `gpio_wdt`, `dw_wdt`, shared Phase 11 wording, or speculative hardware claims.
