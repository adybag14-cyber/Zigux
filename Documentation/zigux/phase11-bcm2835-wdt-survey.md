# Phase 11 BCM2835 Watchdog Survey

This note keeps the current Phase 11 `bcm2835_wdt` lane truthful on `master`.
It stays inside the watchdog family and records the directly reviewable starter packet plus the manifest-backed archival reminder packet that is already present on current `master`, without overclaiming live platform-backed closure.

## Status

* `PHASE11_BCM2835_WDT_SURVEY_STATUS=manifest_landed`
* roadmap phase: `Phase 11`
* archival packet identity remains `P11-L08`, with current continuity tracked through `P11-L10`
* Linux anchor: `drivers/watchdog/bcm2835_wdt.c`
* current bcm2835 state on direct `master` readback is a manifest-backed starter packet with one dedicated replay-backed test surface, one compile-local verify helper, one dedicated survey gate, one remove-time cleanup summary, and one manifest-backed archival reminder packet; the slice note and live platform-backed closure are still not landed

## Current Repo Reality

Current direct `master` readback materializes these bcm2835-local surfaces:

* `drivers/watchdog/bcm2835_wdt.zig`
* `drivers/watchdog/bcm2835_wdt_verify.zig`
* `zigux/tests/phase11_bcm2835_wdt.zig`
* `zigux/tests/phase11_bcm2835_wdt_survey.zig`
* `zigux/tests/phase11_bcm2835_wdt_manifest.json`
* `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
* `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`
* `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`

The current driver file, dedicated replay, compile-local verify helper, survey gate, and manifest-backed archival reminder packet now keep this bounded bcm2835 packet reviewable through:

* heartbeat bounds and tick conversions through `maxTimeoutSeconds()`, `maxHeartbeatMilliseconds()`, `validateHeartbeatSeconds()`, `secondsToWatchdogTicks()`, `watchdogTicksToSeconds()`, and `watchdogTicksToMilliseconds()`
* probe-state and callback-ownership summary through `summarizeProbe()`
* platform-registration and PM-base prerequisite summary through `summarizePlatformHandoff()`
* a bounded runtime model through `Bcm2835WdtLab.init()`, `importBootloaderRunning()`, `getTimeleftSeconds()`, `start()`, `stop()`, `restart()`, `poweroff()`, and `remove()`
* dedicated replay coverage in `zigux/tests/phase11_bcm2835_wdt.zig` for timeout helpers, probe ownership versus handler conflicts, the start-stop-restart-poweroff lifecycle path, and remove cleanup ownership
* compile-local verify coverage in `drivers/watchdog/bcm2835_wdt_verify.zig` for PM-base handoff readiness, claimed-versus-unclaimed poweroff ownership, and claimed-versus-unclaimed remove cleanup intent
* dedicated survey-gate coverage in `zigux/tests/phase11_bcm2835_wdt_survey.zig` for the driver-backed helper surface, the manifest-backed packet markers, and the aligned bcm2835-only reminder notes
* manifest-backed reminder coverage in `zigux/tests/phase11_bcm2835_wdt_manifest.json` for the landed starter, teardown note, validation matrix, and the still-blocked slice-note plus hardware-validation-plan boundary

The next wider bcm2835 packet still remains unlanded on direct readback in this lane:

* `Documentation/zigux/phase11-bcm2835-wdt-slice.md`

## Bounded Meaning

This survey note does not claim:

* live platform registration, PM-base plumbing, watchdog-core registration, or hardware-backed poweroff execution beyond the directly readable helper proofs
* broader shared Phase 11 wording changes outside the bcm2835 packet

It does record one narrower fact: current `master` now keeps a directly readable bcm2835 driver starter, one dedicated replay-backed test surface, one compile-local verify helper, one dedicated survey gate, one bounded remove-time cleanup summary, and one manifest-backed archival reminder packet. That packet is now large enough that the next same-lane move should be one bcm2835-only slice-note extension that matches the manifest-backed starter instead of more stale wording about whether the slice already exists.

## Next Bounded Step

The next honest same-lane follow-through is one bcm2835-only slice-note extension that matches the landed driver starter, verify helper, dedicated replay, dedicated survey gate, manifest, teardown note, and validation matrix.
Keep that follow-through inside the bcm2835 watchdog packet only. Do not widen into `gpio_wdt`, `dw_wdt`, shared Phase 11 wording, or live platform-registration work until that slice-note extension exists.
