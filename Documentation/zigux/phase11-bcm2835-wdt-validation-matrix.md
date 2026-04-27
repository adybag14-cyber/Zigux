# Phase 11 BCM2835 Watchdog Validation Matrix

This document records the first bounded hardware-validation matrix for the Zigux `bcm2835_wdt` lane.

## Status

- `PHASE11_BCM2835_WDT_STATUS=hardware_validation_matrix_landed`
- scope: keep the current `bcm2835_wdt` starter honest about what is already validated, name the next hardware-facing checkpoints, and avoid overclaiming platform registration, PM wiring, or live poweroff coordination before those behaviors exist in Zigux
- current repo reality:
  - `drivers/watchdog/bcm2835_wdt.zig`
  - `zigux/tests/phase11_bcm2835_wdt.zig`
  - `zigux/tests/phase11_bcm2835_wdt_manifest.json`
  - `zigux/tests/phase11_bcm2835_wdt_survey.zig`
  - `zigux/tests/phase11_build.zig`
  - `.github/workflows/zigux-bootstrap.yml`

## Why This Exists

The bounded starter now covers timeout encoding, running-bit detection, start and stop register-image transitions, restart intent, halt-partition bookkeeping, probe-time watchdog-core bookkeeping, registration-facing poweroff ownership outcomes, and remove-time ownership summaries. The live repo still needed one reviewable note that explains:

- which parts of the lane are already exercised by the shared Phase 11 gate
- which platform-facing and hardware-facing checkpoints are the next follow-up rather than live behavior
- which areas must remain out of scope until a later handoff lands

Without this matrix, the slice and survey named the right next step but did not yet preserve the validation posture in one place.

## Hardware-Validation Matrix

| lane surface | current evidence | shared gate today | next bounded follow-up | out of scope for now |
| --- | --- | --- | --- | --- |
| timeout window and register-image transitions | `drivers/watchdog/bcm2835_wdt.zig` validates the 1-15 second timeout window plus `PM_RSTC`, `PM_RSTS`, and `PM_WDOG` register-image transitions through `init()`, `loadRegisters()`, `start()`, `stop()`, and `armRestart()` | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via `zigux/tests/phase11_bcm2835_wdt.zig` in `.github/workflows/zigux-bootstrap.yml` | keep the same timeout and register-image evidence wired into any future platform-registration or PM-base handoff summary | live MMIO access, platform-driver probe, and restart-side effect execution |
| probe-time watchdog-core bookkeeping | `probeSummary()` records bootloader-carried running state, timeout and nowayout initialization, restart priority, stop-on-reboot intent, parent linkage, and system-power-controller eligibility without claiming real watchdog-core calls | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the probe-summary checks in `zigux/tests/phase11_bcm2835_wdt.zig` | add a tiny platform-registration and PM-base handoff summary that keeps probe-time bookkeeping reviewable before any live PM base wiring lands | live watchdog-core registration, PM base acquisition, and backend power-controller integration |
| registration and poweroff ownership boundary | `registrationSummary()` records register-device intent plus poweroff-handler claim-vs-conflict outcomes without claiming `devm_watchdog_register_device()` or a real system poweroff hook | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the registration-summary checks in `zigux/tests/phase11_bcm2835_wdt.zig` | keep the ownership and conflict outcomes stable while the lane grows a tiny platform-registration handoff instead of widening into live poweroff plumbing | real watchdog registration, platform driver binding, and shared handler installation |
| remove-time ownership boundary | `removeSummary()` records when the shared poweroff handler would be cleared only if the bcm2835 lane owns it, while leaving conflicting ownership in place | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the remove-summary checks in `zigux/tests/phase11_bcm2835_wdt.zig` | keep the remove-time ownership evidence tied to the same future platform-registration or PM-base handoff summary | live remove callbacks, reboot-time ordering, and hardware-backed poweroff release |
| platform registration and PM-base behavior | no live Zigux implementation yet; the current repo only records these as the next hardware-facing checkpoint in the slice, survey, and manifest | none beyond the survey and manifest guard that keep the missing work explicit | land one tiny platform-registration and PM-base handoff summary that names registration intent, PM base prerequisites, and poweroff ownership boundaries without claiming MMIO or driver execution | full platform registration, PM base ioremap, watchdog-core lifecycle, suspend or resume handling, and hardware-backed execution |

## Review Rules

- treat this lane as a bounded starter plus validation-note lane until a platform-registration and PM-base handoff actually lands
- keep `zigux/tests/phase11_build.zig` as the shared replay path for the current starter instead of adding ad hoc Phase 11 CI steps
- do not claim PM base wiring, watchdog-core registration, poweroff handler installation, or live restart or poweroff coverage until the Zig surface and tests for those behaviors exist
- when the platform-registration handoff lands, update this matrix, the slice note, the survey note, and the survey manifest together so the lane keeps one truthful next step