# Phase 11 BCM2835 Watchdog Survey

This note keeps the current Phase 11 `bcm2835_wdt` lane truthful on `master`.
It stays inside the watchdog family and records what is directly reviewable now without overclaiming the larger manifest-backed bcm2835 packet that older reminder surfaces still describe.

## Status

* `PHASE11_BCM2835_WDT_SURVEY_STATUS=starter_packet_truthful`
* roadmap phase: `Phase 11`
* archival packet identity remains `P11-L08`
* Linux anchor: `drivers/watchdog/bcm2835_wdt.c`
* current bcm2835 state on direct `master` readback is a bounded starter packet with one dedicated replay-backed test surface, not a full manifest-backed or platform-backed closure packet

## Current Repo Reality

The Phase 11 roadmap still names `drivers/watchdog/bcm2835_wdt.c` as one of the bounded simple production driver anchors beside `gpio_wdt`, `dw_wdt`, and `hvc_console`.

Current direct `master` readback materializes these bcm2835-local surfaces:

* `drivers/watchdog/bcm2835_wdt.zig`
* `zigux/tests/phase11_bcm2835_wdt.zig`
* `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
* `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`
* `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`

The current driver file plus the dedicated replay now keep this bounded starter packet reviewable through:

* heartbeat bounds and tick conversions through `maxTimeoutSeconds()`, `maxHeartbeatMilliseconds()`, `validateHeartbeatSeconds()`, `secondsToWatchdogTicks()`, `watchdogTicksToSeconds()`, and `watchdogTicksToMilliseconds()`
* probe-state and callback-ownership summary through `summarizeProbe()`
* a bounded runtime model through `Bcm2835WdtLab.init()`, `importBootloaderRunning()`, `getTimeleftSeconds()`, `start()`, `stop()`, `restart()`, and `poweroff()`
* dedicated replay coverage in `zigux/tests/phase11_bcm2835_wdt.zig` for timeout helpers, probe ownership versus handler conflicts, and the start-stop-restart-poweroff lifecycle path
* embedded driver-local tests that still mirror the same starter packet from inside `drivers/watchdog/bcm2835_wdt.zig`

At the same time, this run's direct GitHub readback still does not materialize the rest of the archival replay-backed packet that some older reminder notes still imply:

* `zigux/tests/phase11_bcm2835_wdt_manifest.json`
* `zigux/tests/phase11_bcm2835_wdt_survey.zig`
* `drivers/watchdog/bcm2835_wdt_verify.zig`
* `Documentation/zigux/phase11-bcm2835-wdt-slice.md`

That means the honest bcm2835 state is no longer just "the driver starter plus reminder notes." The live state is now one step stronger: a directly readable driver-backed starter plus one dedicated replay file and the bcm2835-local reminder notes exist, while the manifest-backed, survey-gated, and verify-backed packet remains absent on the direct read path used in this run.

## Bounded Meaning

This survey note does not claim:

* a landed bcm2835 manifest-backed packet
* a dedicated survey gate or verify helper that current direct readback can fully materialize
* live platform registration, PM-base plumbing, watchdog-core registration, remove-time cleanup, or hardware-backed poweroff execution

It does record one narrower fact: current `master` now keeps a directly readable bcm2835 driver starter plus one dedicated replay-backed test surface, and the next same-lane work should build outward from that starter-plus-replay packet instead of retelling either the older missing-driver state or a larger landed packet that this run could not read back directly.

## Next Bounded Step

The next honest same-lane follow-through is to add the next bcm2835-only review surface that matches the live driver starter, beginning with one of these extensions only:

* one bcm2835-local manifest or survey-gate surface that matches the directly readable driver starter and replay file
* one compile-local bcm2835 verify helper that keeps restart or poweroff ownership explicit beside the starter packet
* one refresh of another bcm2835-only reminder surface that still describes the pre-replay state

Keep that follow-through inside the bcm2835 watchdog packet only. Do not widen into `gpio_wdt`, `dw_wdt`, shared Phase 11 wording, or speculative platform-registration work until the directly readable bcm2835 packet grows another dedicated proof surface.