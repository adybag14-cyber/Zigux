# Phase 11 BCM2835 Watchdog Validation Matrix

This document records the bounded bcm2835 watchdog validation surface that is directly reviewable on current `master`.
It keeps the current driver-owned packet honest without overclaiming the larger replay-backed bcm2835 packet that older reminder notes still describe.

## Status

- `PHASE11_BCM2835_WDT_STATUS=driver_packet_truthful`
- archival packet identity remains `P11-L08`
- scope: keep the current reviewable bcm2835 driver starter honest about timeout bounds, probe-summary ownership, runtime register modeling, and restart or poweroff intent without claiming dedicated replay files, manifest-backed packet closure, or full platform registration
- this matrix refresh rechecked the directly readable driver and lane-local reminder notes on current `master`; it did not rerun a focused Zig replay from a writable checkout in this environment

## Current Repo Reality

The live bcm2835 watchdog packet directly visible on `master` for this run is:

- `drivers/watchdog/bcm2835_wdt.zig`
- `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
- `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`

The larger bcm2835 packet older notes sometimes imply is still not directly readable through this run's GitHub contents readback:

- `zigux/tests/phase11_bcm2835_wdt.zig`
- `zigux/tests/phase11_bcm2835_wdt_manifest.json`
- `zigux/tests/phase11_bcm2835_wdt_survey.zig`
- `drivers/watchdog/bcm2835_wdt_verify.zig`
- `Documentation/zigux/phase11-bcm2835-wdt-slice.md`

## Directly Reviewable Driver Surface

The current driver file already exposes these bounded review surfaces:

- timeout and conversion helpers: `maxTimeoutSeconds()`, `maxHeartbeatMilliseconds()`, `validateHeartbeatSeconds()`, `secondsToWatchdogTicks()`, `watchdogTicksToSeconds()`, and `watchdogTicksToMilliseconds()`
- probe ownership summary: `summarizeProbe()` plus `ProbeRequest` and `ProbeSummary`
- bounded runtime model: `Bcm2835WdtLab.init()`, `importBootloaderRunning()`, `getTimeleftSeconds()`, `start()`, `stop()`, `restart()`, and `poweroff()`
- embedded driver-local tests:
  - `phase11 bcm2835_wdt conversion helpers keep watchdog bounds explicit`
  - `phase11 bcm2835_wdt probe summary keeps imported running state and poweroff ownership explicit`
  - `phase11 bcm2835_wdt probe summary keeps preexisting poweroff handlers distinct`
  - `phase11 bcm2835_wdt lab start stop and timeleft mirror watchdog register intent`
  - `phase11 bcm2835_wdt restart and poweroff summaries keep full reset and halt partition distinct`

## Driver-Owned Matrix

| surface | current directly readable proof | what stays in scope now | still out of scope |
| --- | --- | --- | --- |
| timeout bounds and conversions | conversion helper functions plus `phase11 bcm2835_wdt conversion helpers keep watchdog bounds explicit` | watchdog tick masks, seconds-to-ticks validation, and bounded time-left conversion behavior | live MMIO writes, watchdog-core registration, and hardware timing |
| probe ownership summary | `summarizeProbe()` plus the two probe-summary tests | nowayout flag readback, bootloader-running import signal, and claimed-versus-conflicting poweroff ownership summary | probe-time platform registration, callback installation, and PM-base wiring |
| start-stop runtime model | `Bcm2835WdtLab.start()`, `stop()`, `getTimeleftSeconds()`, and the start-stop test | programmed tick image, running flag transitions, full-reset bit posture, and time-left derivation | real watchdog register IO, character-device behavior, and broader lifecycle wiring |
| restart and poweroff intent | `Bcm2835WdtLab.restart()`, `poweroff()`, `importBootloaderRunning()`, and the restart-poweroff test | short restart arm path, halt-partition request intent, imported running state, and full-reset request posture | live reboot coordination, shared poweroff callback install, and board-backed shutdown execution |

## Review Guardrails

- Treat this matrix as a truthfulness note for the current directly readable driver-backed starter packet, not as proof that the larger bcm2835 replay packet is fully landed.
- Keep this matrix aligned with `drivers/watchdog/bcm2835_wdt.zig`, `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, and `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md` whenever the directly readable driver helpers or embedded tests change.
- Do not claim dedicated replay files, manifest-backed packet closure, or verify-route coverage until those paths are directly materialized again on the repo read path used in this lane.
- Preserve the archival `P11-L08` packet identity in coupled bcm2835-only reminder surfaces unless a future run explicitly chooses a broader packet-identity rewrite.

## Next Blocked Step

The next honest bcm2835-only follow-through is still one directly readable replay-backed extension that matches the current driver starter. Until that lands, keep this matrix bounded to the driver file and the bcm2835-only reminder notes already visible on `master`.
