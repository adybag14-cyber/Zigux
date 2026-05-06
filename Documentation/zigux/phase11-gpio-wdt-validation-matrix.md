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
  - `Documentation/zigux/phase11-shared-replay-contract.md`
  - `scripts/zigux/check-phase11-shared-replay-contract.py`
  - `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
  - `Documentation/zigux/phase11-gpio-wdt-survey.md`
  - `zigux/tests/README.md`
  - `zigux/Makefile`

## Why This Exists

The bounded starter now covers `hw_algo` parsing, heartbeat-margin validation, the toggle-versus-level runtime transitions, always-running startup, a tiny probe-time summary, a descriptor preflight summary, a nowayout-aware stop helper, and a registration-facing handoff summary. The live repo still needed one reviewable note that explains:

- which parts of the lane are already exercised by the shared Phase 11 gate
- which GPIO-facing and watchdog-core-facing behaviors are already reviewable in bounded form versus still deferred
- which shared replay surfaces on `master` keep this lane aligned with the other shipped Phase 11 starters
- which areas must remain out of scope until a later registration-facing or live GPIO handoff lands

Without this matrix, the slice and survey named the right next step but did not yet preserve the shared replay posture in one place.

## Kernel-Integration Matrix

| lane surface | current evidence | shared gate today | next bounded follow-up | out of scope for now |
| --- | --- | --- | --- | --- |
| property parsing and heartbeat window | `drivers/watchdog/gpio_wdt.zig` validates `hw_algo` parsing, bounded heartbeat margins, the default timeout window, and the exported descriptor through `parseHardwareAlgorithm()`, `initFromPropertyString()`, `init()`, `configSnapshot()`, and `descriptor()` | `zig test --dep gpio_wdt -Mroot=zigux/tests/phase11_gpio_wdt.zig -Mgpio_wdt=drivers/watchdog/gpio_wdt.zig` keeps the property-surface checks in `zigux/tests/phase11_gpio_wdt.zig` on the shipped watchdog replay route | keep the same property and timeout evidence stable while the lane chooses the first registration-facing handoff | devicetree parsing, GPIO descriptor acquisition, platform probe wiring, and hardware-backed heartbeat timing |
| pre-registration startup and line-mode bookkeeping | `probeSummary()` keeps requested line mode, always-running startup, pre-registration running state, parent linkage, timeout init, and stop-on-reboot bookkeeping reviewable before watchdog registration | `zig test --dep gpio_wdt -Mroot=zigux/tests/phase11_gpio_wdt.zig -Mgpio_wdt=drivers/watchdog/gpio_wdt.zig` replays the probe-summary checks in `zigux/tests/phase11_gpio_wdt.zig` through the shared watchdog packet | land one tiny registration-facing note that keeps the same startup bookkeeping explicit at the watchdog-core boundary | live GPIO line requests, watchdog-core registration side effects, and platform-driver lifetime management |
| descriptor preflight | `descriptorPreflightSummary()` records the exact `devm_gpiod_get()` flag choice and the fact that descriptor lookup still sits before timeout parsing, `always-running` bookkeeping, and the registration-facing handoff without claiming a live descriptor call | `zig test --dep gpio_wdt -Mroot=zigux/tests/phase11_gpio_wdt.zig -Mgpio_wdt=drivers/watchdog/gpio_wdt.zig` replays the descriptor-preflight assertions in `zigux/tests/phase11_gpio_wdt.zig` through the shared watchdog packet | if this lane reopens, keep the next step on one tiny timeout-property or drvdata-order checkpoint that stays immediately adjacent to the new descriptor boundary | live GPIO descriptor acquisition, platform-driver registration, and hardware-backed probe execution |
| runtime ping and stop transitions | `start()`, `ping()`, `stop()`, `runtimeSnapshot()`, and the internal disable path keep the toggle-versus-level runtime transitions, pulse bookkeeping, and always-running stop behavior reviewable without claiming live GPIO execution | `zig test --dep gpio_wdt -Mroot=zigux/tests/phase11_gpio_wdt.zig -Mgpio_wdt=drivers/watchdog/gpio_wdt.zig` replays the toggle-mode, level-mode, and stop-path checks in `zigux/tests/phase11_gpio_wdt.zig` through the shared watchdog packet | keep the same runtime transition evidence stable while the lane stays parked on another comparably small host-free handoff | host-backed GPIO writes, hardware pulse timing, and platform reboot integration |
| nowayout-aware stop policy | `requestStop()` keeps watchdog-core `nowayout` blocking distinct from the driver's own always-running hardware behavior, including whether the stop path actually reaches the internal disable helper | `zig test --dep gpio_wdt -Mroot=zigux/tests/phase11_gpio_wdt.zig -Mgpio_wdt=drivers/watchdog/gpio_wdt.zig` replays the stop-request outcome checks in `zigux/tests/phase11_gpio_wdt.zig` through the shared watchdog packet | preserve this stop-policy split in any later watchdog-registration handoff instead of widening straight into watchdog-core glue | live watchdog-core stop callbacks, reboot notifier ordering, and hardware-backed shutdown behavior |
| registration-facing handoff summary | `registrationHandoffSummary()` records what startup state, stop policy, timeout init, and reboot bookkeeping would reach `devm_watchdog_register_device()` without claiming the registration call itself | `zig test --dep gpio_wdt -Mroot=zigux/tests/phase11_gpio_wdt.zig -Mgpio_wdt=drivers/watchdog/gpio_wdt.zig` replays the registration-handoff checks in `zigux/tests/phase11_gpio_wdt.zig` through the shared watchdog packet | use this bounded handoff as the base for the first real registration-surface note rather than widening straight into platform glue | live watchdog registration, parent-device lifetime, GPIO consumer registration, and kernel-managed reboot coordination |
| platform registration and live GPIO behavior | no live Zigux implementation yet; the current repo only records these as the next kernel-facing checkpoint in the slice, survey, manifest, and shared replay contract | none beyond the shared survey and manifest guards that keep the missing work explicit | land one tiny registration-facing or validation-plan note that names device-registration intent, parent ownership, and the first GPIO-backed checkpoint without claiming execution | platform-driver registration, GPIO descriptor acquisition, watchdog-core registration, reboot hooks, and hardware validation coverage |

## Review Rules

- treat this lane as a bounded driver-starter plus validation-note lane until a registration-facing or live GPIO handoff actually lands
- keep `Documentation/zigux/phase11-shared-replay-contract.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `zigux/tests/README.md`, `zigux/tests/phase11_build.zig`, and `zigux/Makefile` aligned so this matrix does not drift away from the shipped shared Phase 11 replay route
- keep `zigux/tests/phase11_build.zig` as the shared replay path for the current starter instead of adding ad hoc Phase 11 CI steps
- do not imply a removed `validate-phase11.py`, a missing `phase11_build_inventory.json` fixture, or a broader checker-script packet that is not on `master`
- do not claim live GPIO descriptor lookup, watchdog-core registration, reboot integration, or hardware-backed execution until the Zig surface and tests for those behaviors exist
- when the next registration-facing or live GPIO handoff lands, update this matrix, the module-slice note, the survey note, and the survey manifest together so the lane keeps one truthful next step
