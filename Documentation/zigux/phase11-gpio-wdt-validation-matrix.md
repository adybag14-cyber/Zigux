# Phase 11 GPIO Watchdog Validation Matrix

This document records the first bounded hardware-validation matrix for the Zigux `gpio_wdt` lane.

## Status

- `PHASE11_GPIO_WDT_STATUS=registration_preflight_landed`
- scope: keep the current `gpio_wdt` starter honest about what is already validated, name the current metadata-only registration evidence, and avoid overclaiming live GPIO, platform registration, or reboot integration before those behaviors exist in Zigux
- current repo reality:
  - `drivers/watchdog/gpio_wdt.zig`
  - `zigux/tests/phase11_gpio_wdt.zig`
  - `zigux/tests/phase11_gpio_wdt_manifest.json`
  - `zigux/tests/phase11_gpio_wdt_survey.zig`
  - `zigux/tests/phase11_build.zig`
  - `.github/workflows/zigux-bootstrap.yml`

## Why This Exists

The bounded starter now covers `hw_algo` parsing, heartbeat-margin validation, start or ping or stop transitions, a small probe-time summary, a nowayout-aware stop helper, and a registration-facing handoff summary. The live repo still needed one reviewable note that explains:

- which parts of the lane are already exercised by the shared Phase 11 gate
- which registration-facing checkpoints are now metadata-only evidence rather than live behavior
- which areas must remain out of scope until a later `devm_watchdog_register_device()` call-surface helper lands

Without this matrix, the slice and survey named the right next step but did not yet preserve the validation posture in one place.

## Hardware-Validation Matrix

| lane surface | current evidence | shared gate today | next bounded follow-up | out of scope for now |
| --- | --- | --- | --- | --- |
| property parsing and bounded timeout window | `drivers/watchdog/gpio_wdt.zig` validates `toggle` versus `level` mode selection plus the same bounded heartbeat-margin window used by `drivers/watchdog/gpio_wdt.c` through `init()` and `initFromPropertyString()` | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via `zigux/tests/phase11_gpio_wdt.zig` in `.github/workflows/zigux-bootstrap.yml` | keep the same property and timeout evidence wired into any later registration-facing surface | live GPIO descriptor lookup, module parameter wiring, and platform-driver execution |
| in-memory start, ping, and stop transitions | `GpioWatchdogLab.start()`, `ping()`, `stop()`, and `requestStop()` keep toggle-state, pulse-count, disable-count, and nowayout-versus-always-running outcomes reviewable without claiming hardware-backed toggling | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the transition and stop-policy checks in `zigux/tests/phase11_gpio_wdt.zig` | keep the same stop-policy and nowayout failure-mode evidence stable while the lane advances to the first bounded `devm_watchdog_register_device()` call surface | live GPIO value changes, reboot hooks, and watchdog-core stop side effects |
| probe-time startup bookkeeping | `probeSummary()` records requested line mode, `always-running` startup behavior, parent linkage, timeout-init intent, `stop_on_reboot`, and pre-registration running state without claiming real GPIO or watchdog-core calls | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the probe-summary checks in `zigux/tests/phase11_gpio_wdt.zig` | keep the probe bookkeeping explicit while a later lane decides whether descriptor acquisition or registration intent is the first real boundary to widen | live probe callbacks, devm-managed GPIO acquisition, and watchdog-core registration |
| registration-facing handoff summary | `registrationHandoffSummary()` keeps startup state, line mode, timeout-init intent, stop policy, and reboot bookkeeping reviewable as metadata that would reach `devm_watchdog_register_device()` without claiming the registration call itself | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the registration handoff assertions in `zigux/tests/phase11_gpio_wdt.zig` | add one tiny `devm_watchdog_register_device()` call-surface summary so watchdog-device metadata ownership stays explicit before any GPIO descriptor acquisition or reboot glue lands | real platform registration, `devm_gpiod_get()`, `devm_watchdog_register_device()`, and hardware-backed execution |

## Shared Replay Surface

- current shared replay wiring on `master` includes both `phase11-gpio-wdt-tests` and `phase11-gpio-wdt-survey-tests`
- exact shared command:
  - `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
- included gpio artifacts:
  - `phase11-gpio-wdt-tests`
  - `phase11-gpio-wdt-survey-tests`
- focused survey replay command:
  - `zig test zigux/tests/phase11_gpio_wdt_survey.zig`

## Review Rules

- treat this lane as a bounded starter plus validation-matrix lane even after the registration-facing handoff summary lands
- keep `zigux/tests/phase11_build.zig` as the shared replay path for the current starter instead of adding ad hoc Phase 11 CI steps
- do not claim GPIO descriptor lookup, watchdog-core registration, reboot glue, or live hardware validation until the Zig surface and tests for those behaviors exist
- if a later lane advances to the first bounded `devm_watchdog_register_device()` call surface, update this matrix, the slice note, the survey note, and the survey manifest together so the lane keeps one truthful next step