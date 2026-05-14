# Phase 11 BCM2835 Watchdog Survey

This note keeps the current Phase 11 `bcm2835_wdt` lane truthful on `master`.
It stays inside the watchdog family and records what is directly readable now without overclaiming the larger bcm2835 packet that older reminder surfaces still describe.

## Status

* `PHASE11_BCM2835_WDT_SURVEY_STATUS=starter_packet_truthful`
* roadmap phase: `Phase 11`
* archival packet identity remains `P11-L08`
* Linux anchor: `drivers/watchdog/bcm2835_wdt.c`
* current bcm2835 state on direct `master` readback is a bounded partial starter packet, not a full replay-backed or platform-backed closure packet

## Current Repo Reality

The Phase 11 roadmap still names `drivers/watchdog/bcm2835_wdt.c` as one of the bounded simple production driver anchors beside `gpio_wdt`, `dw_wdt`, and `hvc_console`.

Current direct `master` readback does materialize these bcm2835-local reminder surfaces:

* `drivers/watchdog/bcm2835_wdt.zig`
* `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
* `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`
* `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`

The current driver file already keeps a small directly readable starter packet around:

* heartbeat bounds and tick conversions through `maxTimeoutSeconds()`, `maxHeartbeatMilliseconds()`, `validateHeartbeatSeconds()`, `secondsToWatchdogTicks()`, `watchdogTicksToSeconds()`, and `watchdogTicksToMilliseconds()`
* probe-state and callback-ownership summary through `summarizeProbe()`
* a bounded runtime model through `Bcm2835WdtLab.init()`, `importBootloaderRunning()`, `getTimeleftSeconds()`, `start()`, `stop()`, `restart()`, and `poweroff()`
* embedded driver-local tests for bounds, probe-summary ownership, start-stop behavior, and restart-plus-poweroff behavior

At the same time, this run's direct GitHub readback still does not materialize several larger packet surfaces that some older reminder notes and checker paths still imply:

* `zigux/tests/phase11_bcm2835_wdt.zig`
* `zigux/tests/phase11_bcm2835_wdt_manifest.json`
* `zigux/tests/phase11_bcm2835_wdt_survey.zig`
* `drivers/watchdog/bcm2835_wdt_verify.zig`
* `Documentation/zigux/phase11-bcm2835-wdt-slice.md`

That means the honest bcm2835 state is no longer "the driver starter is entirely missing," but it is also not "the full replay-backed packet is landed." The live state is narrower: a directly readable driver-backed starter plus lane-local reminder notes exist, while the dedicated replay, manifest, and verify surfaces remain absent on the direct read path used in this run.

## Bounded Meaning

This survey note does not claim:

* a landed dedicated bcm2835 replay file under `zigux/tests/`
* a manifest-backed or checker-backed bcm2835 packet that current direct readback can fully materialize
* live platform registration, PM-base plumbing, watchdog-core registration, remove-time cleanup, or hardware-backed poweroff execution

It does record one narrower fact: current `master` now keeps a directly readable bcm2835 driver starter with embedded tests and lane-local reminder notes, and the next same-lane work should build outward from that partial packet instead of retelling either the older missing-driver state or a larger landed packet that this run could not read back directly.

## Next Bounded Step

The next honest same-lane follow-through is to add the first dedicated bcm2835 replay-backed surface that matches the live driver starter, beginning with one of these bcm2835-local extensions only:

* one dedicated replay file under `zigux/tests/`
* one bcm2835-local manifest or checker surface that matches the directly readable driver starter
* one refresh of another bcm2835-only reminder surface that still describes replay files the current direct read path cannot materialize

Keep that follow-through inside the bcm2835 watchdog packet only. Do not widen into `gpio_wdt`, `dw_wdt`, shared Phase 11 wording, or speculative platform-registration work until the directly readable bcm2835 replay packet actually exists.
