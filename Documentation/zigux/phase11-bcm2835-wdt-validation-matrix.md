# Phase 11 BCM2835 Watchdog Validation Matrix

This document records the bounded bcm2835 watchdog validation surface that is directly reviewable on current `master`.
It keeps the current starter packet honest while now including dedicated survey-gate coverage and the already-landed manifest-backed reminder packet, without overclaiming live platform-backed closure.

## Status

- `PHASE11_BCM2835_WDT_STATUS=manifest_truthful`
- archival packet identity remains `P11-L08`, with current continuity tracked through `P11-L10`
- scope: keep the current reviewable bcm2835 starter honest about timeout bounds, probe-summary ownership, runtime register modeling, restart or poweroff intent, compile-local verify coverage, dedicated survey-gate coverage, and the manifest-backed reminder packet, without claiming live platform registration or full platform-backed closure
- this matrix refresh rechecked the directly readable driver, dedicated replay, verify helper, dedicated survey gate, manifest, teardown note, and bcm2835-only reminder notes on current `master`; it did not rerun a broader shared Phase 11 build from a writable checkout in this environment

## Current Repo Reality

The live bcm2835 watchdog packet directly visible on `master` for this run is:

- `drivers/watchdog/bcm2835_wdt.zig`
- `drivers/watchdog/bcm2835_wdt_verify.zig`
- `zigux/tests/phase11_bcm2835_wdt.zig`
- `zigux/tests/phase11_bcm2835_wdt_survey.zig`
- `zigux/tests/phase11_bcm2835_wdt_manifest.json`
- `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
- `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`

The next wider bcm2835 packet still not directly readable through this lane is:

- `Documentation/zigux/phase11-bcm2835-wdt-slice.md`

## Directly Reviewable Driver Surface

The current driver file plus the dedicated replay, verify helper, survey gate, and manifest-backed reminder packet now expose these bounded review surfaces:

- timeout and conversion helpers: `maxTimeoutSeconds()`, `maxHeartbeatMilliseconds()`, `validateHeartbeatSeconds()`, `secondsToWatchdogTicks()`, `watchdogTicksToSeconds()`, and `watchdogTicksToMilliseconds()`
- probe ownership summary: `summarizeProbe()` plus `ProbeRequest` and `ProbeSummary`
- PM-base and platform-registration prerequisite summary: `summarizePlatformHandoff()` plus `PlatformHandoffRequest` and `PlatformHandoffSummary`
- bounded runtime model: `Bcm2835WdtLab.init()`, `importBootloaderRunning()`, `getTimeleftSeconds()`, `start()`, `stop()`, `restart()`, `poweroff()`, and `remove()`
- dedicated replay tests in `zigux/tests/phase11_bcm2835_wdt.zig`
- compile-local verify tests in `drivers/watchdog/bcm2835_wdt_verify.zig`
- dedicated survey-gate checks in `zigux/tests/phase11_bcm2835_wdt_survey.zig`
- packet truth manifest checks in `zigux/tests/phase11_bcm2835_wdt_manifest.json`

## Driver-Owned Matrix

| surface | current directly readable proof | what stays in scope now | still out of scope |
| --- | --- | --- | --- |
| timeout bounds and conversions | driver helper functions plus the dedicated replay and survey-gate coverage | watchdog tick masks, seconds-to-ticks validation, and bounded time-left conversion behavior | live MMIO writes, watchdog-core registration, and hardware timing |
| probe and PM-base handoff summary | `summarizeProbe()`, `summarizePlatformHandoff()`, the dedicated replay, the compile-local verify helper, and the dedicated survey gate | nowayout flag readback, bootloader-running import signal, PM-base readiness, and claimed-versus-conflicting poweroff ownership summary | live platform registration, callback installation, and PM-base execution wiring |
| start-stop runtime model | `Bcm2835WdtLab.start()`, `stop()`, `restart()`, `poweroff()`, and `remove()` plus the dedicated replay | programmed tick image, running-flag transitions, full-reset bit posture, restart-or-poweroff intent, and remove cleanup ownership | real watchdog register IO, character-device behavior, and board-backed shutdown execution |
| dedicated review packet alignment | `zigux/tests/phase11_bcm2835_wdt_survey.zig`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`, and this matrix | bcm2835-only truthfulness for the directly readable driver, replay, verify helper, teardown note, and manifest-backed reminder packet | claiming a landed slice note, live platform registration, or broader shared Phase 11 wording |

## Review Guardrails

- Treat this matrix as a truthfulness note for the current directly readable starter packet, dedicated replay, compile-local verify helper, dedicated survey gate, and manifest-backed reminder packet, not as proof of live platform-backed closure.
- Keep this matrix aligned with `drivers/watchdog/bcm2835_wdt.zig`, `drivers/watchdog/bcm2835_wdt_verify.zig`, `zigux/tests/phase11_bcm2835_wdt.zig`, `zigux/tests/phase11_bcm2835_wdt_survey.zig`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, and `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md` whenever the directly readable helpers or reminder packet changes.
- Do not claim a landed slice note, live platform registration, PM-base plumbing, watchdog-core registration, or hardware-backed poweroff execution until the bcm2835 lane records those wider packet surfaces explicitly.

## Next Blocked Step

The next honest bcm2835-only follow-through is one slice-note extension that matches the current starter-plus-replay-plus-verify-plus-survey-plus-manifest packet. Until that lands, keep this matrix bounded to the directly readable bcm2835 surfaces already visible on `master`.
