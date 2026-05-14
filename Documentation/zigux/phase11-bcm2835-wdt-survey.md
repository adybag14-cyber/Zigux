# Phase 11 BCM2835 Watchdog Survey

This note keeps the current Phase 11 `bcm2835_wdt` lane truthful on `master`.
It stays inside the watchdog family and records what is directly readable now plus the bcm2835 replay surfaces that the shared Phase 11 contract already names as raw-fallback materialized, without overclaiming a larger manifest-backed bcm2835 packet.

## Status

* `PHASE11_BCM2835_WDT_SURVEY_STATUS=starter_packet_truthful`
* roadmap phase: `Phase 11`
* archival packet identity remains `P11-L08`
* Linux anchor: `drivers/watchdog/bcm2835_wdt.c`
* current bcm2835 state on direct `master` readback is a bounded starter packet with raw-fallback replay support, not a full manifest-backed or platform-backed closure packet

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

The shared Phase 11 contract also records these bcm2835-local replay surfaces as raw-fallback materialized on current `master`:

* `zigux/tests/phase11_bcm2835_wdt.zig`
* `drivers/watchdog/bcm2835_wdt_verify.zig`
* `zigux/tests/phase11_build.zig`

At the same time, this run's direct GitHub readback still does not materialize the rest of the archival replay-backed packet that some older reminder notes still imply:

* `zigux/tests/phase11_bcm2835_wdt_manifest.json`
* `zigux/tests/phase11_bcm2835_wdt_survey.zig`
* `Documentation/zigux/phase11-bcm2835-wdt-slice.md`

That means the honest bcm2835 state is no longer "the driver starter is entirely missing," and it is also no longer "the replay and verify route is absent." The live state is narrower: a directly readable driver-backed starter plus a raw-fallback replay and verify route exist, while the manifest-backed survey closure surfaces remain absent on the direct read path used in this run.

## Bounded Meaning

This survey note does not claim:

* a manifest-backed or checker-backed bcm2835 packet that current direct readback can fully materialize end to end
* live platform registration, PM-base plumbing, watchdog-core registration, remove-time cleanup, or hardware-backed poweroff execution

It does record one narrower fact: current `master` now keeps a directly readable bcm2835 driver starter, a shared-contract-backed raw replay file, and a verify route beside the lane-local reminder notes, and the next same-lane work should build outward from that partial packet instead of retelling either the older missing-driver state or a larger landed packet that this run could not read back directly.

## Next Bounded Step

The next honest same-lane follow-through is to add the first bcm2835-local manifest, survey-gate, or checker surface that matches the already materialized driver, replay, and verify route, beginning with one of these bcm2835-local extensions only:

* one bcm2835-local manifest or survey gate under `zigux/tests/`
* one bcm2835-local checker or reminder surface that names the existing replay and verify route without pretending the whole archival packet is directly readable
* one refresh of another bcm2835-only reminder surface that still describes the replay or verify route as absent

Keep that follow-through inside the bcm2835 watchdog packet only. Do not widen into `gpio_wdt`, `dw_wdt`, shared Phase 11 wording, or speculative platform-registration work until the directly readable bcm2835 packet grows a truthful manifest-backed closure surface.
