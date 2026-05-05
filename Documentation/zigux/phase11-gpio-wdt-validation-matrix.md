# Phase 11 GPIO Watchdog Validation Matrix

This document records the first bounded hardware-validation matrix for the Zigux `gpio_wdt` lane.

## Status

- `PHASE11_GPIO_WDT_STATUS=hardware_validation_matrix_landed`
- scope: keep the current `gpio_wdt` starter honest about what is already validated, name the next kernel-facing checkpoints, and avoid overclaiming platform registration or live GPIO behavior before those surfaces exist in Zigux
- current repo reality:
  - `drivers/watchdog/gpio_wdt.zig`
  - `zigux/tests/phase11_gpio_wdt.zig`
  - `zigux/tests/phase11_gpio_wdt_manifest.json`
  - `zigux/tests/phase11_gpio_wdt_survey.zig`
  - `zigux/tests/phase11_build.zig`
  - `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
  - `Documentation/zigux/phase11-gpio-wdt-survey.md`

## Why This Exists

The bounded starter now covers `hw_algo` parsing, heartbeat-margin validation, the toggle-versus-level runtime transitions, always-running startup, a tiny probe-time summary, a nowayout-aware stop helper, and a registration-facing handoff summary. The live repo still needed one reviewable note that explains:

- which parts of the lane are already exercised by the shared Phase 11 gate
- which GPIO-facing and watchdog-core-facing behaviors are already reviewable in bounded form versus still deferred
- which areas must remain out of scope until a later registration-facing or live GPIO handoff lands

Without this matrix, the slice and survey named the right next step but did not yet preserve the validation posture in one place.

## Kernel-Integration Matrix

| lane surface | current evidence | shared gate today | next bounded follow-up | out of scope for now |
| --- | --- | --- | --- | --- |
| property parsing and heartbeat window | `drivers/watchdog/gpio_wdt.zig` validates `hw_algo` parsing, bounded heartbeat margins, the default timeout window, and the exported descriptor through `parseHardwareAlgorithm()`, `initFromPropertyString()`, `init()`, `configSnapshot()`, and `descriptor()` | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the descriptor and property-surface checks in `zigux/tests/phase11_gpio_wdt.zig` | keep the same property and timeout evidence stable while the lane chooses the first registration-facing handoff | devicetree parsing, GPIO descriptor acquisition, platform probe wiring, and hardware-backed heartbeat timing |
| pre-registration startup and line-mode bookkeeping | `probeSummary()` keeps requested line mode, always-running startup, pre-registration running state, parent linkage, timeout init, and stop-on-reboot bookkeeping reviewable before watchdog registration | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the probe-summary checks in `zigux/tests/phase11_gpio_wdt.zig` | land one tiny registration-facing note that keeps the same startup bookkeeping explicit at the watchdog-core boundary | live GPIO line requests, watchdog-core registration side effects, and platform-driver lifetime management |
| runtime ping and stop transitions | `start()`, `ping()`, `stop()`, `runtimeSnapshot()`, and the internal disable path keep the toggle-versus-level runtime transitions, pulse bookkeeping, and always-running stop behavior reviewable without claiming live GPIO execution | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the toggle-mode, level-mode, and stop-path checks in `zigux/tests/phase11_gpio_wdt.zig` | keep the same runtime transition evidence stable while the lane stays parked on another comparably small host-free handoff | host-backed GPIO writes, hardware pulse timing, and platform reboot integration |
| nowayout-aware stop policy | `requestStop()` keeps watchdog-core `nowayout` blocking distinct from the driver’s own always-running hardware behavior, including whether the stop path actually reaches the internal disable helper | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the stop-request outcome checks in `zigux/tests/phase11_gpio_wdt.zig` | preserve this stop-policy split in any later watchdog-registration handoff instead of widening straight into watchdog-core glue | live watchdog-core stop callbacks, reboot notifier ordering, and hardware-backed shutdown behavior |
| registration-facing handoff summary | `registrationHandoffSummary()` records what startup state, stop policy, timeout init, and reboot bookkeeping would reach `devm_watchdog_register_device()` without claiming the registration call itself | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the registration-handoff checks in `zigux/tests/phase11_gpio_wdt.zig` | use this bounded handoff as the base for the first real registration-surface note rather than widening straight into platform glue | live watchdog registration, parent-device lifetime, GPIO consumer registration, and kernel-managed reboot coordination |
| platform registration and live GPIO behavior | no live Zigux implementation yet; the current repo only records these as the next kernel-facing checkpoint in the slice, survey, and manifest | none beyond the survey or manifest guard that keeps the missing work explicit | land one tiny registration-facing or validation-plan note that names device-registration intent, parent ownership, and the first GPIO-backed checkpoint without claiming execution | platform-driver registration, GPIO descriptor acquisition, watchdog-core registration, reboot hooks, and hardware validation coverage |

## Review Rules

- treat this lane as a bounded driver-starter plus validation-note lane until a registration-facing or live GPIO handoff actually lands
- keep `zigux/tests/phase11_build.zig` as the shared replay path for the current starter instead of adding ad hoc Phase 11 CI steps
- do not claim platform-driver registration, GPIO descriptor lookup, watchdog-core registration, reboot integration, or hardware-backed execution until the Zig surface and tests for those behaviors exist
- when the next registration-facing or live GPIO handoff lands, update this matrix, the module-slice note, the survey note, and the survey manifest together so the lane keeps one truthful next step
