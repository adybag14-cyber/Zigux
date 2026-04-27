# Phase 11 BCM2835 Watchdog Validation Matrix

This document records the first bounded hardware-validation matrix for the Zigux `bcm2835_wdt` lane.

## Status

- `PHASE11_BCM2835_WDT_STATUS=platform_handoff_landed`
- scope: keep the current `bcm2835_wdt` starter honest about what is already validated, name the current platform-handoff evidence, and avoid overclaiming live platform registration, PM wiring, or poweroff coordination before those behaviors exist in Zigux
- current repo reality:
  - `drivers/watchdog/bcm2835_wdt.zig`
  - `zigux/tests/phase11_bcm2835_wdt.zig`
  - `zigux/tests/phase11_bcm2835_wdt_manifest.json`
  - `zigux/tests/phase11_bcm2835_wdt_survey.zig`
  - `zigux/tests/phase11_build.zig`
  - `.github/workflows/zigux-bootstrap.yml`

## Why This Exists

The bounded starter now covers timeout encoding, running-bit detection, start and stop register-image transitions, restart intent, halt-partition bookkeeping, probe-time watchdog-core bookkeeping, registration-facing poweroff ownership outcomes, a tiny platform-registration and PM-base handoff summary, and remove-time ownership summaries. The live repo still needs one reviewable note that explains:

- which parts of the lane are already exercised by the shared Phase 11 gate
- which platform-facing and hardware-facing checkpoints are the next follow-up rather than live behavior
- which areas must remain out of scope until a later handoff lands

Without this matrix, the slice and survey named the right next step but did not yet preserve the validation posture in one place.

## Hardware-Validation Matrix

| lane surface | current evidence | shared gate today | next bounded follow-up | out of scope for now |
| --- | --- | --- | --- | --- |
| timeout window and register-image transitions | `drivers/watchdog/bcm2835_wdt.zig` validates the 1-15 second timeout window plus `PM_RSTC`, `PM_RSTS`, and `PM_WDOG` register-image transitions through `init()`, `loadRegisters()`, `start()`, `stop()`, and `armRestart()` | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via `zigux/tests/phase11_bcm2835_wdt.zig` in `.github/workflows/zigux-bootstrap.yml` | keep the same timeout and register-image evidence wired into any later live platform-registration choice | live MMIO access, platform-driver probe, and restart-side effect execution |
| probe-time watchdog-core bookkeeping | `probeSummary()` records bootloader-carried running state, timeout and nowayout initialization, restart priority, stop-on-reboot intent, parent linkage, and system-power-controller eligibility without claiming real watchdog-core calls | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the probe-summary checks in `zigux/tests/phase11_bcm2835_wdt.zig` | keep the probe bookkeeping stable while any later lane decides whether PM base wiring is worth widening into | live watchdog-core registration, PM base acquisition, and backend power-controller integration |
| registration and poweroff ownership boundary | `registrationSummary()` records register-device intent plus poweroff-handler claim-vs-conflict outcomes without claiming `devm_watchdog_register_device()` or a real system poweroff hook | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the registration-summary checks in `zigux/tests/phase11_bcm2835_wdt.zig` | keep the ownership and conflict outcomes stable while live platform registration stays blocked | real watchdog registration, platform driver binding, and shared handler installation |
| platform registration and PM-base handoff | `platformHandoffSummary()` now records parent attachment, PM-base availability, drvdata handoff readiness, register-device intent, and poweroff claim-vs-conflict reviewability without claiming platform-driver execution or live MMIO | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the platform-handoff checks in `zigux/tests/phase11_bcm2835_wdt.zig` | keep the handoff summary honest while a future lane decides whether to model any live platform registration or PM base plumbing | full platform registration, PM base ioremap, watchdog-core lifecycle, suspend or resume handling, and hardware-backed execution |
| remove-time ownership boundary | `removeSummary()` records when the shared poweroff handler would be cleared only if the bcm2835 lane owns it, while leaving conflicting ownership in place | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the remove-summary checks in `zigux/tests/phase11_bcm2835_wdt.zig` | keep the remove-time ownership evidence tied to the same later live platform decision rather than widening this starter lane further | live remove callbacks, reboot-time ordering, and hardware-backed poweroff release |

## Review Rules

- treat this lane as a bounded starter plus validation-note lane even after the platform-registration and PM-base handoff summary lands
- keep `zigux/tests/phase11_build.zig` as the shared replay path for the current starter instead of adding ad hoc Phase 11 CI steps
- do not claim PM base wiring, watchdog-core registration, poweroff handler installation, or live restart or poweroff coverage until the Zig surface and tests for those behaviors exist
- if a later lane chooses live platform registration or PM base plumbing, update this matrix, the slice note, the survey note, and the survey manifest together so the lane keeps one truthful next step
