# Phase 11 GPIO Watchdog Validation Matrix

This document records the first bounded hardware-validation matrix for the Zigux `gpio_wdt` lane.

## Status

- `PHASE11_GPIO_WDT_STATUS=hardware_validation_matrix_landed`
- scope: keep the current `gpio_wdt` starter honest about what is already validated, name the remaining registration, teardown, failure-mode, and hardware-backed validation gap, and avoid overclaiming platform registration or live GPIO behavior before those surfaces exist in Zigux
- current repo reality:
  - `drivers/watchdog/gpio_wdt.zig`
  - `zigux/tests/phase11_gpio_wdt.zig`
  - `zigux/tests/phase11_gpio_wdt_manifest.json`
  - `zigux/tests/phase11_gpio_wdt_survey.zig`
  - `zigux/tests/phase11_build.zig`
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/review-checklist.md`
  - `Documentation/zigux/phase11-shared-replay-contract.md`
  - `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
  - `Documentation/zigux/phase11-gpio-wdt-survey.md`
  - `Documentation/zigux/phase11-uapi-header-parity-survey.md`
  - `scripts/zigux/README.md`
  - `scripts/zigux/check-phase11-shared-replay-contract.py`
  - `scripts/zigux/check-phase11-header-boundary-packet.py`
  - `zigux/tests/README.md`
  - `zigux/Makefile`
  - `.github/workflows/zigux-bootstrap.yml`

## Why This Exists

The bounded starter now covers `hw_algo` parsing, heartbeat-margin validation, the toggle-versus-level runtime transitions, always-running startup, a tiny probe-time summary, a descriptor preflight summary, a timeout-property checkpoint, a nowayout-aware stop helper, and a registration-facing handoff summary. The live shared Phase 11 packet already couples those gpio-specific replays to `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/README.md`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`, which keep the focused shared header-boundary packet and the wider shared build route explicit beside this watchdog-local matrix. This matrix keeps one reviewable note that explains:

- which parts of the lane are already exercised by the shared Phase 11 gate
- which GPIO-facing and watchdog-core-facing behaviors are already reviewable in bounded form versus still deferred
- which shared replay surfaces on `master` keep this lane aligned with the other shipped Phase 11 starters
- which registration, teardown, failure-mode, and hardware-backed validation areas must remain out of scope until a later handoff lands

Without this matrix, the slice and survey named the right next step but did not yet preserve the shared replay posture in one place.

## Kernel-Integration Matrix

| lane surface | current evidence | shared gate today | next bounded follow-up | out of scope for now |
| --- | --- | --- | --- | --- |
| property parsing and heartbeat window | `drivers/watchdog/gpio_wdt.zig` validates `hw_algo` parsing, bounded heartbeat margins, the default timeout window, and the exported descriptor through `parseHardwareAlgorithm()`, `initFromPropertyString()`, `init()`, `configSnapshot()`, and `descriptor()` | `zig test --dep gpio_wdt -Mroot=zigux/tests/phase11_gpio_wdt.zig -Mgpio_wdt=drivers/watchdog/gpio_wdt.zig` keeps the property-surface checks in `zigux/tests/phase11_gpio_wdt.zig` on the shipped watchdog replay route | keep the same property and timeout evidence stable while the lane chooses the first registration-facing scaffold that preserves the remaining teardown and failure-mode parity plan | devicetree parsing, GPIO descriptor acquisition, platform probe wiring, and hardware-backed heartbeat timing |
| pre-registration startup and line-mode bookkeeping | `probeSummary()` keeps requested line mode, always-running startup, pre-registration running state, parent linkage, timeout init, and stop-on-reboot bookkeeping reviewable before watchdog registration | `zig test --dep gpio_wdt -Mroot=zigux/tests/phase11_gpio_wdt.zig -Mgpio_wdt=drivers/watchdog/gpio_wdt.zig` replays the probe-summary checks in `zigux/tests/phase11_gpio_wdt.zig` through the shared watchdog packet | land one registration-facing scaffold note that keeps the same startup bookkeeping explicit at the watchdog-core boundary and names the later teardown and failure-mode parity checkpoints | live GPIO line requests, watchdog-core registration side effects, and platform-driver lifetime management |
| descriptor preflight | `descriptorPreflightSummary()` records the exact `devm_gpiod_get()` flag choice and the fact that descriptor lookup still sits before timeout parsing, `always-running` bookkeeping, and the registration-facing handoff without claiming a live descriptor call | `zig test --dep gpio_wdt -Mroot=zigux/tests/phase11_gpio_wdt.zig -Mgpio_wdt=drivers/watchdog/gpio_wdt.zig` replays the descriptor-preflight assertions in `zigux/tests/phase11_gpio_wdt.zig` through the shared watchdog packet | keep the next step on one registration-facing scaffold that stays adjacent to the descriptor boundary while still preserving the remaining teardown and failure-mode parity plan | live GPIO descriptor acquisition, platform-driver registration, and hardware-backed probe execution |
| timeout-property checkpoint | `timeoutPropertyCheckpointSummary()` now records that `hw_margin_ms` stays required and bounds-checked after descriptor lookup but before `always-running` bookkeeping, `watchdog_set_drvdata()`, and the registration-facing handoff, and it keeps the invalid-timeout failure gate explicit without claiming a live property read | `zig test --dep gpio_wdt -Mroot=zigux/tests/phase11_gpio_wdt.zig -Mgpio_wdt=drivers/watchdog/gpio_wdt.zig` replays the timeout-property checkpoint assertions in `zigux/tests/phase11_gpio_wdt.zig` through the shared watchdog packet | keep the next step on one registration-facing scaffold that ties the timeout boundary to `watchdog_set_drvdata()`, the later teardown and failure-mode parity checkpoints, and the eventual hardware-backed validation route | live property reads, live GPIO descriptor acquisition, platform-driver registration, and hardware-backed probe execution |
| runtime ping and stop transitions | `start()`, `ping()`, `stop()`, `runtimeSnapshot()`, and the internal disable path keep the toggle-versus-level runtime transitions, pulse bookkeeping, and always-running stop behavior reviewable without claiming live GPIO execution | `zig test --dep gpio_wdt -Mroot=zigux/tests/phase11_gpio_wdt.zig -Mgpio_wdt=drivers/watchdog/gpio_wdt.zig` replays the toggle-mode, level-mode, and stop-path checks in `zigux/tests/phase11_gpio_wdt.zig` through the shared watchdog packet | keep the same runtime transition evidence stable while the lane stays parked on the first registration-facing scaffold and the still-missing teardown and failure-mode parity packet | host-backed GPIO writes, hardware pulse timing, and platform reboot integration |
| nowayout-aware stop policy | `requestStop()` keeps watchdog-core `nowayout` blocking distinct from the driver's own always-running hardware behavior, including whether the stop path actually reaches the internal disable helper | `zig test --dep gpio_wdt -Mroot=zigux/tests/phase11_gpio_wdt.zig -Mgpio_wdt=drivers/watchdog/gpio_wdt.zig` replays the stop-request outcome checks in `zigux/tests/phase11_gpio_wdt.zig` through the shared watchdog packet | preserve this stop-policy split in any later registration scaffold instead of widening straight into watchdog-core glue, and keep the later teardown and failure-mode parity packet explicit | live watchdog-core stop callbacks, reboot notifier ordering, and hardware-backed shutdown behavior |
| registration-facing handoff summary | `registrationHandoffSummary()` records what startup state, stop policy, timeout init, and reboot bookkeeping would reach `devm_watchdog_register_device()` without claiming the registration call itself | `zig test --dep gpio_wdt -Mroot=zigux/tests/phase11_gpio_wdt.zig -Mgpio_wdt=drivers/watchdog/gpio_wdt.zig` replays the registration-handoff checks in `zigux/tests/phase11_gpio_wdt.zig` through the shared watchdog packet | use this bounded handoff as the base for the first real registration-surface note that also names the remaining teardown and failure-mode parity plus hardware-backed validation checkpoints | live watchdog registration, parent-device lifetime, GPIO consumer registration, and kernel-managed reboot coordination |
| platform registration and live GPIO behavior | no live Zigux implementation yet; the current repo only records these as the next kernel-facing checkpoint in the slice, survey, manifest, and shared replay contract | none beyond the shared survey and manifest guards that keep the missing work explicit | land one registration-facing scaffold note or replay that names descriptor acquisition, drvdata handoff, watchdog registration, teardown and failure-mode parity, and hardware-backed validation checkpoints without claiming execution | platform-driver registration, GPIO descriptor acquisition, watchdog-core registration, reboot hooks, and hardware validation coverage |

## Review Rules

- treat this lane as a bounded driver-starter plus validation-note lane until a registration-facing or live GPIO handoff actually lands
- keep `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/README.md`, `zigux/tests/phase11_build.zig`, and `zigux/Makefile` aligned so this matrix does not drift away from the shipped shared Phase 11 replay route or the focused shared header-boundary packet
- keep `zigux/tests/phase11_build.zig` as the shared replay path for the current starter instead of adding ad hoc Phase 11 CI steps
- do not imply a removed `validate-phase11.py`, a missing `phase11_build_inventory.json` fixture, or a broader checker-script packet that is not on `master`
- do not claim live GPIO descriptor lookup, watchdog-core registration, reboot integration, or hardware-backed execution until the Zig surface and tests for those behaviors exist
- when the next registration-facing, teardown-parity, failure-mode, or hardware-validation handoff lands, update this matrix, the module-slice note, the survey note, and the survey manifest together so the lane keeps one truthful next step
