# Phase 11 BCM2835 Watchdog Survey

This note keeps the current Phase 11 `bcm2835_wdt` lane truthful on `master`.
It stays inside the watchdog family and records the directly reviewable starter packet plus the dedicated replay, verify, and survey surfaces, without overclaiming a fully manifest-backed bcm2835 closure packet.

## Status

* `PHASE11_BCM2835_WDT_SURVEY_STATUS=survey_gate_landed`
* roadmap phase: `Phase 11`
* archival packet identity remains `P11-L08`
* Linux anchor: `drivers/watchdog/bcm2835_wdt.c`
* current bcm2835 state on direct `master` readback is a bounded starter packet with one dedicated replay-backed test surface, one compile-local verify helper, one dedicated survey gate, and one remove-time cleanup summary; the larger manifest-backed slice note and full platform-backed closure packet are still not landed

## Current Repo Reality

Current direct `master` readback materializes these bcm2835-local surfaces:

* `drivers/watchdog/bcm2835_wdt.zig`
* `drivers/watchdog/bcm2835_wdt_verify.zig`
* `zigux/tests/phase11_bcm2835_wdt.zig`
* `zigux/tests/phase11_bcm2835_wdt_survey.zig`
* `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
* `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`
* `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`

The current driver file, dedicated replay, compile-local verify helper, and survey gate now keep this bounded starter packet reviewable through:

* heartbeat bounds and tick conversions through `maxTimeoutSeconds()`, `maxHeartbeatMilliseconds()`, `validateHeartbeatSeconds()`, `secondsToWatchdogTicks()`, `watchdogTicksToSeconds()`, and `watchdogTicksToMilliseconds()`
* probe-state and callback-ownership summary through `summarizeProbe()`
* platform-registration and PM-base prerequisite summary through `summarizePlatformHandoff()`
* a bounded runtime model through `Bcm2835WdtLab.init()`, `importBootloaderRunning()`, `getTimeleftSeconds()`, `start()`, `stop()`, `restart()`, `poweroff()`, and `remove()`
* dedicated replay coverage in `zigux/tests/phase11_bcm2835_wdt.zig` for timeout helpers, probe ownership versus handler conflicts, the start-stop-restart-poweroff lifecycle path, and remove cleanup ownership
* compile-local verify coverage in `drivers/watchdog/bcm2835_wdt_verify.zig` for PM-base handoff readiness, claimed-versus-unclaimed poweroff ownership, and claimed-versus-unclaimed remove cleanup intent
* dedicated survey-gate coverage in `zigux/tests/phase11_bcm2835_wdt_survey.zig` for the driver-backed helper surface and the aligned bcm2835-only reminder notes

The next wider bcm2835 packet still remains unlanded on direct readback in this lane:

* `zigux/tests/phase11_bcm2835_wdt_manifest.json`
* `Documentation/zigux/phase11-bcm2835-wdt-slice.md`

## Bounded Meaning

This survey note does not claim:

* a landed bcm2835 manifest-backed closure packet
* live platform registration, PM-base plumbing, watchdog-core registration, or hardware-backed poweroff execution beyond the directly readable helper proofs
* broader shared Phase 11 wording changes outside the bcm2835 packet

It does record one narrower fact: current `master` now keeps a directly readable bcm2835 driver starter, one dedicated replay-backed test surface, one compile-local verify helper, one dedicated survey gate, and one bounded remove-time cleanup summary, so the next same-lane work should build outward from that proof packet instead of retelling either the older missing-survey state or a larger landed packet that is still not directly readable in this lane.

## Next Bounded Step

The next honest same-lane follow-through is one bcm2835-only manifest or slice-note extension that matches the now directly readable driver starter, verify helper, dedicated replay, dedicated survey gate, and remove cleanup summary.
Keep that follow-through inside the bcm2835 watchdog packet only. Do not widen into `gpio_wdt`, `dw_wdt`, shared Phase 11 wording, or speculative platform-registration work until the directly readable bcm2835 packet grows another dedicated proof surface.
