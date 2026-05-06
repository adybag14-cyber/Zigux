# Phase 11 BCM2835 Watchdog Validation Matrix

This document records the first bounded hardware-validation matrix for the Zigux `bcm2835_wdt` lane.

## Status

- `PHASE11_BCM2835_WDT_STATUS=platform_handoff_landed`
- reviewed against live `master` `55568844ac3ce835b0e0bef624c24c17f22b78a1`
- archival packet identity remains `P11-L08`, while current scheduled continuity for this archived bcm2835 watchdog packet is tracked through `P11-L10`; keep later DesignWare follow-up on `P11-L11`
- scope: keep the current `bcm2835_wdt` starter honest about what is already validated, name the current timeout-window and register-image evidence alongside the registration-outcome, platform-handoff, poweroff-path, and remove-time callback-identity evidence, and avoid overclaiming live platform registration, PM wiring, or poweroff coordination before those behaviors exist in Zigux
- latest focused replays: `zig test zigux/tests/phase11_bcm2835_wdt.zig`, `zig test drivers/watchdog/bcm2835_wdt_verify.zig`, and `zig test zigux/tests/phase11_bcm2835_wdt_survey.zig` still pass for the bounded bcm2835 packet on current `master`
- shared replay boundary: `zig build test --build-file zigux/tests/phase11_build.zig --summary all` still includes `phase11-bcm2835-wdt-tests`, `phase11-bcm2835-wdt-verify-tests`, and `phase11-bcm2835-wdt-survey-tests`, but this watchdog-local matrix no longer claims that the whole current shared Phase 11 replay is green when unrelated non-watchdog drift can reopen elsewhere on `master`
- current repo reality:
  - `drivers/watchdog/bcm2835_wdt.zig`
  - `drivers/watchdog/bcm2835_wdt_verify.zig`
  - `zigux/tests/phase11_bcm2835_wdt.zig`
  - `zigux/tests/phase11_bcm2835_wdt_manifest.json`
  - `zigux/tests/phase11_bcm2835_wdt_survey.zig`
  - `zigux/tests/phase11_build.zig`
  - `.github/workflows/zigux-bootstrap.yml`

## Why This Exists

The bounded starter now covers watchdog metadata, timeout encoding, running-bit detection, start and stop register-image transitions, restart intent, halt-partition bookkeeping, probe-time watchdog-core bookkeeping, registration-facing poweroff ownership outcomes, a tiny registration-outcome summary for register-device success-versus-failure and probe-error blocking, a tiny platform-registration and PM-base handoff summary, a tiny poweroff-path summary, and remove-time teardown summaries. The live repo still needs one reviewable note that explains:

- which parts of the lane are already exercised by the shared Phase 11 gate
- which platform-facing and hardware-facing checkpoints are the next follow-up rather than live behavior
- which areas must remain out of scope until a later handoff lands

Without this matrix, the slice and survey named the right next step but did not yet preserve the validation posture in one place.

## Hardware-Validation Matrix

| lane surface | current evidence | shared gate today | next bounded follow-up | out of scope for now |
| --- | --- | --- | --- | --- |
| watchdog metadata surface | `watchdogMetadataSummary()` records the Linux watchdog identity string, the `WDIOF_SETTIMEOUT`, `WDIOF_MAGICCLOSE`, and `WDIOF_KEEPALIVEPING` option coverage, the bounded start or stop or get_timeleft or restart ops surface, and the static timeout bounds from `bcm2835_wdt_wdd` without claiming real watchdog-core registration | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the watchdog-metadata checks in `zigux/tests/phase11_bcm2835_wdt.zig` | keep the metadata summary aligned with any later platform-registration decision so the bounded starter still exposes the same Linux-facing contract before live registration exists | real watchdog-core registration, live watchdog_info wiring, and hardware-backed ioctl exposure |
| timeout window and register-image transitions | `drivers/watchdog/bcm2835_wdt.zig` validates the 1-15 second timeout window plus `PM_RSTC`, `PM_RSTS`, and `PM_WDOG` register-image transitions through `init()`, `loadRegisters()`, `start()`, `stop()`, and `armRestart()` | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via `zigux/tests/phase11_bcm2835_wdt.zig` in `.github/workflows/zigux-bootstrap.yml` | keep the same timeout and register-image transition evidence wired into any later live platform-registration choice | live MMIO access, platform-driver probe, and restart-side effect execution |
| probe-time watchdog-core bookkeeping | `probeSummary()` records bootloader-carried running state, timeout and nowayout initialization, restart priority, stop-on-reboot intent, parent linkage, and system-power-controller eligibility without claiming real watchdog-core calls | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the probe-summary checks in `zigux/tests/phase11_bcm2835_wdt.zig` | keep the probe bookkeeping stable while any later lane decides whether PM base wiring is worth widening into | live watchdog-core registration, PM base acquisition, and backend power-controller integration |
| registration and poweroff ownership boundary | `registrationSummary()` records register-device intent plus poweroff-handler claim-vs-conflict outcomes without claiming `devm_watchdog_register_device()` or a real system poweroff hook | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the registration-summary checks in `zigux/tests/phase11_bcm2835_wdt.zig` | keep the ownership and conflict outcomes stable while live platform registration stays blocked | real watchdog registration, platform driver binding, and shared handler installation |
| registration outcome failure boundary | `registrationOutcomeSummary()` records register-device success versus failure, probe-error return intent, and whether the bcm2835 lane can claim or must leave the shared poweroff handler alone when registration does not complete, without claiming a live `devm_watchdog_register_device()` result path | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the registration-outcome checks in `zigux/tests/phase11_bcm2835_wdt.zig` | keep the success-versus-failure split aligned with any later platform-registration decision so probe error handling and poweroff ownership do not get blurred together | live watchdog registration failure injection, platform probe return behavior, and hardware-backed rollback |
| platform registration and PM-base handoff | `platformHandoffSummary()` now records parent attachment, PM-base availability, drvdata handoff readiness, register-device intent, and poweroff claim-vs-conflict reviewability without claiming platform-driver execution or live MMIO | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the platform-handoff checks in `zigux/tests/phase11_bcm2835_wdt.zig` | keep the handoff summary honest while a future lane decides whether to model any live platform registration or PM base plumbing | full platform registration, PM base ioremap, watchdog-core lifecycle, suspend or resume handling, and hardware-backed execution |
| poweroff path summary | `poweroffSummary()` records the shared system-poweroff callback ownership preconditions, writes the Raspberry Pi halt-partition bits into `PM_RSTS`, and reuses the short watchdog restart arming sequence only when the bcm2835 lane currently owns the callback | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the poweroff-summary checks in `zigux/tests/phase11_bcm2835_wdt.zig` | keep the poweroff-path summary tied to the same later platform or PM-base decision rather than widening into callback installation | live poweroff callback registration, PM base wiring, and hardware-backed shutdown execution |
| remove-time teardown boundary | `removeSummary()` records that watchdog teardown stays devm-managed while the explicit remove callback only clears the shared poweroff callback when `pm_power_off` still matches `bcm2835_power_off`, leaving conflicting or unrelated callback ownership in place | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the remove-summary checks in `zigux/tests/phase11_bcm2835_wdt.zig` | keep the remove-time teardown scope tied to the same later live platform decision rather than widening this starter lane further | live remove callbacks beyond ownership cleanup, reboot-time ordering, and hardware-backed poweroff release |

## Shared Replay Surface

- current shared replay wiring on `master` includes `phase11-bcm2835-wdt-tests`, `phase11-bcm2835-wdt-verify-tests`, and `phase11-bcm2835-wdt-survey-tests`
- exact shared command:
  - `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
- shared replay posture for this watchdog lane:
  - `phase11-bcm2835-wdt-tests`, `phase11-bcm2835-wdt-verify-tests`, and `phase11-bcm2835-wdt-survey-tests` remain the shared Phase 11 artifacts that cover this bcm2835 packet
  - full-bundle green status for the wider current Phase 11 replay is intentionally tracked outside this watchdog-local matrix because unrelated non-watchdog drift can reopen elsewhere on `master`
- included bcm2835 artifacts:
  - `phase11-bcm2835-wdt-tests`
  - `phase11-bcm2835-wdt-verify-tests`
  - `phase11-bcm2835-wdt-survey-tests`
- focused survey replay command:
  - `zig test zigux/tests/phase11_bcm2835_wdt_survey.zig`

## Review Rules

- treat this lane as a bounded starter plus validation-note lane even after the platform-registration and PM-base handoff summary lands
- keep `zigux/tests/phase11_build.zig` as the shared replay path for the current starter instead of adding ad hoc Phase 11 CI steps
- do not claim PM base wiring, watchdog-core registration, poweroff handler installation, or live restart or poweroff coverage until the Zig surface and tests for those behaviors exist
- if a later lane chooses live platform registration or PM base plumbing, update this matrix, the slice note, the survey note, and the survey manifest together so the lane keeps one truthful next step
