# Phase 11 BCM2835 Watchdog Validation Matrix

This document records the bounded bcm2835 watchdog validation surface that is directly reviewable on current `master`.
It keeps the current starter packet honest while now including dedicated survey-gate coverage, without overclaiming a fully manifest-backed bcm2835 closure packet.

## Status

- `PHASE11_BCM2835_WDT_STATUS=survey_gate_truthful`
- archival packet identity remains `P11-L08`
- scope: keep the current reviewable bcm2835 starter honest about timeout bounds, probe-summary ownership, runtime register modeling, restart or poweroff intent, compile-local verify coverage, and dedicated survey-gate coverage, without claiming manifest-backed closure or full platform registration
- this matrix refresh rechecked the directly readable driver, dedicated replay, verify helper, dedicated survey gate, and bcm2835-only reminder notes on current `master`; it did not rerun a broader shared Phase 11 build from a writable checkout in this environment

## Current Repo Reality

The live bcm2835 watchdog packet directly visible on `master` for this run is:

- `drivers/watchdog/bcm2835_wdt.zig`
- `drivers/watchdog/bcm2835_wdt_verify.zig`
- `zigux/tests/phase11_bcm2835_wdt.zig`
- `zigux/tests/phase11_bcm2835_wdt_survey.zig`
- `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
- `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`

The next wider bcm2835 packet still not directly readable through this lane is:

- `zigux/tests/phase11_bcm2835_wdt_manifest.json`
- `Documentation/zigux/phase11-bcm2835-wdt-slice.md`

## Directly Reviewable Driver Surface

The current driver file plus the dedicated replay, verify helper, and survey gate now expose these bounded review surfaces:

- timeout and conversion helpers: `maxTimeoutSeconds()`, `maxHeartbeatMilliseconds()`, `validateHeartbeatSeconds()`, `secondsToWatchdogTicks()`, `watchdogTicksToSeconds()`, and `watchdogTicksToMilliseconds()`
- probe ownership summary: `summarizeProbe()` plus `ProbeRequest` and `ProbeSummary`
- PM-base and platform-registration prerequisite summary: `summarizePlatformHandoff()` plus `PlatformHandoffRequest` and `PlatformHandoffSummary`
- bounded runtime model: `Bcm2835WdtLab.init()`, `importBootloaderRunning()`, `getTimeleftSeconds()`, `start()`, `stop()`, `restart()`, and `poweroff()`
- dedicated replay tests in `zigux/tests/phase11_bcm2835_wdt.zig`
- compile-local verify tests in `drivers/watchdog/bcm2835_wdt_verify.zig`
- dedicated survey-gate checks in `zigux/tests/phase11_bcm2835_wdt_survey.zig`

## Driver-Owned Matrix

| surface | current directly readable proof | what stays in scope now | still out of scope |
| --- | --- | --- | --- |
| timeout bounds and conversions | driver helper functions plus the dedicated replay and survey-gate coverage | watchdog tick masks, seconds-to-ticks validation, and bounded time-left conversion behavior | live MMIO writes, watchdog-core registration, and hardware timing |
| probe and PM-base handoff summary | `summarizeProbe()`, `summarizePlatformHandoff()`, the dedicated replay, the compile-local verify helper, and the dedicated survey gate | nowayout flag readback, bootloader-running import signal, PM-base readiness, and claimed-versus-conflicting poweroff ownership summary | live platform registration, callback installation, and PM-base execution wiring |
| start-stop runtime model | `Bcm2835WdtLab.start()`, `stop()`, `restart()`, `poweroff()`, and the dedicated replay | programmed tick image, running-flag transitions, full-reset bit posture, and restart-or-poweroff intent | real watchdog register IO, character-device behavior, and board-backed shutdown execution |
| dedicated review packet alignment | `zigux/tests/phase11_bcm2835_wdt_survey.zig`, `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, and this matrix | bcm2835-only truthfulness for the directly readable driver, replay, and verify helper packet | manifest-backed closure and broader shared Phase 11 wording |

## Review Guardrails

- Treat this matrix as a truthfulness note for the current directly readable starter packet, dedicated replay, compile-local verify helper, and dedicated survey gate, not as proof that the larger bcm2835 packet is fully landed.
- Keep this matrix aligned with `drivers/watchdog/bcm2835_wdt.zig`, `drivers/watchdog/bcm2835_wdt_verify.zig`, `zigux/tests/phase11_bcm2835_wdt.zig`, `zigux/tests/phase11_bcm2835_wdt_survey.zig`, `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, and `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md` whenever the directly readable helpers or replay change.
- Do not claim `zigux/tests/phase11_bcm2835_wdt_manifest.json` or `Documentation/zigux/phase11-bcm2835-wdt-slice.md` as landed until those bcm2835-only packet surfaces are directly materialized.
- Preserve the archival `P11-L08` packet identity in coupled bcm2835-only reminder surfaces unless a future run explicitly chooses a broader packet-identity rewrite.

## Next Blocked Step

The next honest bcm2835-only follow-through is one manifest-backed or slice-note extension that matches the current starter-plus-replay-plus-verify-plus-survey packet. Until that lands, keep this matrix bounded to the directly readable bcm2835 surfaces already visible on `master`.
