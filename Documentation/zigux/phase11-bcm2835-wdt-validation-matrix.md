# Phase 11 BCM2835 Watchdog Validation Matrix

This document records the bounded bcm2835 watchdog validation surface that is directly reviewable on current `master`.
It keeps the current driver-owned packet honest without overclaiming the larger manifest-backed bcm2835 packet that older reminder notes still describe, while also naming the raw-fallback replay route already recorded by the shared Phase 11 contract.

## Status

- `PHASE11_BCM2835_WDT_STATUS=driver_packet_truthful`
- archival packet identity remains `P11-L08`
- scope: keep the current reviewable bcm2835 driver starter honest about timeout bounds, probe-summary ownership, runtime register modeling, restart or poweroff intent, and the already recorded raw-fallback replay route without claiming manifest-backed packet closure or full platform registration
- this matrix refresh rechecked the directly readable driver and lane-local reminder notes on current `master`; it did not rerun a focused Zig replay from a writable checkout in this environment

## Current Repo Reality

The live bcm2835 watchdog packet directly visible on `master` for this run is:

- `drivers/watchdog/bcm2835_wdt.zig`
- `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
- `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`

The shared Phase 11 contract also records these bcm2835-local replay surfaces as raw-fallback materialized on current `master`:

- `zigux/tests/phase11_bcm2835_wdt.zig`
- `drivers/watchdog/bcm2835_wdt_verify.zig`
- `zigux/tests/phase11_build.zig`

The larger bcm2835 packet older notes sometimes imply is still not directly readable through this run's GitHub contents readback:

- `zigux/tests/phase11_bcm2835_wdt_manifest.json`
- `zigux/tests/phase11_bcm2835_wdt_survey.zig`
- `Documentation/zigux/phase11-bcm2835-wdt-slice.md`

## Driver And Raw-Fallback Replay Surface

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
- shared-contract-backed replay route:
  - `zigux/tests/phase11_bcm2835_wdt.zig`
  - `drivers/watchdog/bcm2835_wdt_verify.zig`
  - `zigux/tests/phase11_build.zig`

## Driver-Owned Matrix

| surface | current directly readable proof | what stays in scope now | still out of scope |
| --- | --- | --- | --- |
| timeout bounds and conversions | conversion helper functions plus `phase11 bcm2835_wdt conversion helpers keep watchdog bounds explicit` | watchdog tick masks, seconds-to-ticks validation, and bounded time-left conversion behavior | live MMIO writes, watchdog-core registration, and hardware timing |
| probe ownership summary | `summarizeProbe()` plus the two probe-summary tests | nowayout flag readback, bootloader-running import signal, and claimed-versus-conflicting poweroff ownership summary | probe-time platform registration, callback installation, and PM-base wiring |
| start-stop runtime model | `Bcm2835WdtLab.start()`, `stop()`, `getTimeleftSeconds()`, and the start-stop test | programmed tick image, running flag transitions, full-reset bit posture, and time-left derivation | real watchdog register IO, character-device behavior, and broader lifecycle wiring |
| restart and poweroff intent | `Bcm2835WdtLab.restart()`, `poweroff()`, `importBootloaderRunning()`, and the restart-poweroff test | short restart arm path, halt-partition request intent, imported running state, and full-reset request posture | live reboot coordination, shared poweroff callback install, and board-backed shutdown execution |
| replay and verify route presence | the shared Phase 11 contract plus the named replay and verify paths | reviewable evidence that the bcm2835 packet already has one raw-fallback replay file, one verify route, and the shared Phase 11 build path beside the driver-owned starter | manifest-backed survey closure, directly readable end-to-end packet materialization, and broader platform-backed validation |

## Review Guardrails

- Treat this matrix as a truthfulness note for the current directly readable driver-backed starter plus the raw-fallback replay route, not as proof that the larger manifest-backed bcm2835 packet is fully landed.
- Keep this matrix aligned with `drivers/watchdog/bcm2835_wdt.zig`, `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, and `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md` whenever the directly readable driver helpers or embedded tests change.
- Do not claim manifest-backed survey closure, dedicated checker closure, or end-to-end packet materialization until those paths are directly readable or explicitly refreshed in this lane.
- Preserve the archival `P11-L08` packet identity in coupled bcm2835-only reminder surfaces unless a future run explicitly chooses a broader packet-identity rewrite.

## Next Blocked Step

The next honest bcm2835-only follow-through is one manifest-backed, survey-gated, or checker-backed extension that matches the current driver starter plus the already recorded replay route. Until that lands, keep this matrix bounded to the driver file, the shared-contract replay markers, and the bcm2835-only reminder notes already visible on `master`.
