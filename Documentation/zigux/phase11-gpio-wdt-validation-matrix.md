# Phase 11 GPIO Watchdog Validation Matrix

This document records the first bounded hardware-validation matrix for the Zigux `gpio_wdt` lane.

## Status

- `PHASE11_GPIO_WDT_STATUS=hardware_validation_matrix_landed`
- scope: keep the current `gpio_wdt` starter honest about what is already validated, name the remaining registration, teardown, failure-mode, and hardware-backed validation gap, and avoid overclaiming platform registration or live GPIO behavior before those surfaces exist in Zigux
- current repo reality:
  - `drivers/watchdog/gpio_wdt.zig`
  - `zigux/tests/phase11_gpio_wdt.zig`
  - `zigux/tests/phase11_gpio_wdt_platform_drvdata.zig`
  - `zigux/tests/phase11_gpio_wdt_manifest.json`
  - `zigux/tests/phase11_gpio_wdt_survey.zig`
  - `zigux/tests/phase11_build.zig`
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/review-checklist.md`
  - `Documentation/zigux/phase11-shared-replay-contract.md`
  - `Documentation/zigux/phase11-closure-note.md`
  - `Documentation/zigux/phase11-driver-lane-sequencing.md`
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

The bounded starter now covers `hw_algo` parsing, heartbeat-margin validation, the toggle-versus-level runtime transitions, always-running startup, a tiny probe-time summary, a descriptor preflight summary, a timeout-property checkpoint, a platform drvdata checkpoint, a drvdata checkpoint, a nowayout-aware stop helper, a registration-facing handoff summary, a register-device call summary, and a bounded teardown summary. The live shared Phase 11 packet already couples the gpio-specific shared replays to `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-closure-note.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/README.md`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`, while `zigux/tests/phase11_gpio_wdt_platform_drvdata.zig` stays a focused local replay beside that shared route. This matrix keeps one reviewable note that explains:

- which parts of the lane are already exercised by the shared Phase 11 gate
- which focused local replay surfaces still sit beside the shared Phase 11 gate because they are not yet wired into `phase11_build.zig`
- which GPIO-facing and watchdog-core-facing behaviors are already reviewable in bounded form versus still deferred
- which shared replay surfaces on `master` keep this lane aligned with the other shipped Phase 11 starters
- which registration, teardown, failure-mode, and hardware-backed validation areas must remain out of scope until a later handoff lands

Without this matrix, the slice and survey named the right next step but did not yet preserve the platform-drvdata evidence posture in one place.

## Kernel-Integration Matrix

| lane surface | current evidence | shared gate today | next bounded follow-up | out of scope for now |
| --- | --- | --- | --- | --- |
| property parsing and heartbeat window | `drivers/watchdog/gpio_wdt.zig` validates `hw_algo` parsing, bounded heartbeat margins, the default timeout window, and the exported descriptor through `parseHardwareAlgorithm()`, `initFromPropertyString()`, `init()`, `configSnapshot()`, and `descriptor()` | `zig test --dep gpio_wdt -Mroot=zigux/tests/phase11_gpio_wdt.zig -Mgpio_wdt=drivers/watchdog/gpio_wdt.zig` keeps the property-surface checks in `zigux/tests/phase11_gpio_wdt.zig` on the shipped watchdog replay route | keep the same property and timeout evidence stable while the lane chooses the first registration-facing scaffold that preserves the remaining teardown and failure-mode parity plan | devicetree parsing, GPIO descriptor acquisition, platform probe wiring, and hardware-backed heartbeat timing |
| pre-registration startup and line-mode bookkeeping | `probeSummary()` keeps requested line mode, always-running startup, pre-registration running state, parent linkage, timeout init, and stop-on-reboot bookkeeping reviewable before watchdog registration | `zig test --dep gpio_wdt -Mroot=zigux/tests/phase11_gpio_wdt.zig -Mgpio_wdt=drivers/watchdog/gpio_wdt.zig` replays the probe-summary checks in `zigux/tests/phase11_gpio_wdt.zig` through the shared watchdog packet | land one registration-facing scaffold note that keeps the same startup bookkeeping explicit at the watchdog-core boundary and names the later teardown and failure-mode parity checkpoints | live GPIO line requests, watchdog-core registration side effects, and platform-driver lifetime management |
| descriptor preflight | `descriptorPreflightSummary()` records the exact `devm_gpiod_get()` flag choice and the fact that descriptor lookup still sits before timeout parsing, `always-running` bookkeeping, and the registration-facing handoff without claiming a live descriptor call | `zig test --dep gpio_wdt -Mroot=zigux/tests/phase11_gpio_wdt.zig -Mgpio_wdt=drivers/watchdog/gpio_wdt.zig` replays the descriptor-preflight assertions in `zigux/tests/phase11_gpio_wdt.zig` through the shared watchdog packet | keep the next step on one registration-facing scaffold that stays adjacent to the descriptor boundary while still preserving the remaining teardown and failure-mode parity plan | live GPIO descriptor acquisition, platform-driver registration, and hardware-backed probe execution |
| timeout-property checkpoint | `timeoutPropertyCheckpointSummary()` now records that `hw_margin_ms` stays required and bounds-checked after descriptor lookup but before `always-running` bookkeeping, `watchdog_set_drvdata()`, and the registration-facing handoff, and it keeps the invalid-timeout failure gate explicit without claiming a live property read | `zig test --dep gpio_wdt -Mroot=zigux/tests/phase11_gpio_wdt.zig -Mgpio_wdt=drivers/watchdog/gpio_wdt.zig` replays the timeout-property checkpoint assertions in `zigux/tests/phase11_gpio_wdt.zig` through the shared watchdog packet | keep the next step on one registration-facing scaffold that ties the timeout boundary to `watchdog_set_drvdata()`, the later teardown and failure-mode parity checkpoints, and the eventual hardware-backed validation route | live property reads, live GPIO descriptor acquisition, platform-driver registration, and hardware-backed probe execution |
| platform drvdata checkpoint | `platformDrvdataCheckpointSummary()` records that allocation is followed by `platform_set_drvdata()` before `hw_algo` parsing, descriptor lookup, timeout-property handling, and the later `watchdog_set_drvdata()` handoff without claiming a live platform probe | focused local replay `zig test zigux/tests/phase11_gpio_wdt_platform_drvdata.zig` keeps the dedicated checkpoint honest while the shared Phase 11 route stays unchanged | keep this early ordering evidence traceable beside the shared packet until a later lane decides whether the checkpoint should join broader platform-registration work | live platform probing, live `platform_set_drvdata()` execution, live GPIO lookup, and hardware-backed probe execution |
| drvdata checkpoint | `drvdataCheckpointSummary()` records that descriptor lookup and the required `hw_margin_ms` property still precede `watchdog_set_drvdata()`, and that the drvdata handoff itself stays required before both the registration-facing handoff and the first `devm_watchdog_register_device()` request surface without claiming execution | `zig test --dep gpio_wdt -Mroot=zigux/tests/phase11_gpio_wdt.zig -Mgpio_wdt=drivers/watchdog/gpio_wdt.zig` replays the drvdata-checkpoint assertions in `zigux/tests/phase11_gpio_wdt.zig` through the shared watchdog packet | keep the next step on one registration-facing scaffold that preserves the `watchdog_set_drvdata()` boundary while still naming the later teardown and failure-mode parity checkpoints | live `watchdog_set_drvdata()` execution, live GPIO descriptor acquisition, platform-driver registration, and hardware-backed probe execution |
| runtime ping and stop transitions | `start()`, `ping()`, `stop()`, `runtimeSnapshot()`, and the internal disable path keep the toggle-versus-level runtime transitions, pulse bookkeeping, and always-running stop behavior reviewable without claiming live GPIO execution | `zig test --dep gpio_wdt -Mroot=zigux/tests/phase11_gpio_wdt.zig -Mgpio_wdt=drivers/watchdog/gpio_wdt.zig` replays the toggle-mode, level-mode, and stop-path checks in `zigux/tests/phase11_gpio_wdt.zig` through the shared watchdog packet | keep the same runtime transition evidence stable while the lane stays parked on the first registration-facing scaffold and the still-missing teardown and failure-mode parity packet | host-backed GPIO writes, hardware pulse timing, and platform reboot integration |
| nowayout-aware stop policy | `requestStop()` keeps watchdog-core `nowayout` blocking distinct from the driver's own always-running hardware behavior, including whether the stop path actually reaches the internal disable helper | `zig test --dep gpio_wdt -Mroot=zigux/tests/phase11_gpio_wdt.zig -Mgpio_wdt=drivers/watchdog/gpio_wdt.zig` replays the stop-request outcome checks in `zigux/tests/phase11_gpio_wdt.zig` through the shared watchdog packet | preserve this stop-policy split in any later registration scaffold instead of widening straight into watchdog-core glue, and keep the later teardown and failure-mode parity packet explicit | live watchdog-core stop callbacks, reboot notifier ordering, and hardware-backed shutdown behavior |
| registration-facing handoff summary | `registrationHandoffSummary()` records what startup state, stop policy, timeout init, and reboot bookkeeping would reach `devm_watchdog_register_device()` without claiming the registration call itself | `zig test --dep gpio_wdt -Mroot=zigux/tests/phase11_gpio_wdt.zig -Mgpio_wdt=drivers/watchdog/gpio_wdt.zig` replays the registration-handoff checks in `zigux/tests/phase11_gpio_wdt.zig` through the shared watchdog packet | use this bounded handoff as the base for the first real registration-surface note that also names the remaining teardown and failure-mode parity plus hardware-backed validation checkpoints | live watchdog registration, parent-device lifetime, GPIO consumer registration, and kernel-managed reboot coordination |
| register-device request surface | `registerDeviceCallSummary()` records the first bounded `devm_watchdog_register_device()` request surface, including descriptor readiness, timeout propagation, `watchdog_set_drvdata()` completion, parent linkage, `nowayout`, and the still-blocked live GPIO, platform-registration, and reboot-glue boundaries without claiming execution | `zig test --dep gpio_wdt -Mroot=zigux/tests/phase11_gpio_wdt.zig -Mgpio_wdt=drivers/watchdog/gpio_wdt.zig` replays the register-device request assertions in `zigux/tests/phase11_gpio_wdt.zig` through the shared watchdog packet | keep this request surface traceable while later same-family lanes decide whether teardown-facing parity or hardware-backed validation can move forward without claiming live registration | live `devm_watchdog_register_device()` execution, live GPIO descriptor ownership, reboot callbacks, and hardware-backed probe or remove behavior |
| teardown posture | `teardownSummary()` records the bounded stopped, always-running, and nowayout-blocked outcomes so the starter can describe teardown-facing stop policy without claiming remove hooks or broader failure-mode coverage | `zig test --dep gpio_wdt -Mroot=zigux/tests/phase11_gpio_wdt.zig -Mgpio_wdt=drivers/watchdog/gpio_wdt.zig` replays the teardown-summary assertions in `zigux/tests/phase11_gpio_wdt.zig` through the shared watchdog packet | keep this bounded teardown posture explicit while later same-family lanes decide whether to widen into remove-hook parity or broader failure-mode replay | remove hooks, shutdown ordering, reboot notifier teardown, and hardware-backed teardown behavior |
| platform registration and live GPIO behavior | no live Zigux implementation yet; the current repo only records these as the next kernel-facing checkpoint after the landed descriptor, timeout-property, platform-drvdata, drvdata, handoff, register-device request, and bounded teardown summaries | none beyond the shared survey and manifest guards that keep the missing work explicit | land one later same-family scaffold note or replay that names descriptor acquisition, platform and watchdog drvdata handoffs, watchdog registration, teardown and failure-mode parity, and hardware-backed validation checkpoints without claiming execution | platform-driver registration, GPIO descriptor acquisition, watchdog-core registration, reboot hooks, and hardware validation coverage |

## Shared Replay Surface

- current shared replay wiring on `master` includes `phase11-gpio-wdt-tests` and `phase11-gpio-wdt-survey-tests`
- focused local replay that stays outside `zigux/tests/phase11_build.zig` today:
  - `zig test zigux/tests/phase11_gpio_wdt_platform_drvdata.zig`
- exact shared commands:
  - `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
  - `make -C zigux phase11`
- shared replay posture for this watchdog lane:
  - `phase11-gpio-wdt-tests` and `phase11-gpio-wdt-survey-tests` remain the shared Phase 11 artifacts that cover this gpio packet
  - the focused shared header-boundary packet from `Documentation/zigux/phase11-uapi-header-parity-survey.md` plus `scripts/zigux/check-phase11-header-boundary-packet.py` stays explicit beside those gpio-local replays inside the same shipped Phase 11 route
  - `zigux/tests/phase11_gpio_wdt_platform_drvdata.zig` is intentionally tracked as focused local evidence rather than shared-build green status
  - full-bundle green status for the wider current Phase 11 replay is intentionally tracked outside this gpio-local matrix because unrelated non-watchdog drift can reopen elsewhere on `master`
- included gpio artifacts:
  - `phase11-gpio-wdt-tests`
  - `phase11-gpio-wdt-survey-tests`
- focused survey replay command:
  - `zig test zigux/tests/phase11_gpio_wdt_survey.zig`
- focused platform-drvdata replay command:
  - `zig test zigux/tests/phase11_gpio_wdt_platform_drvdata.zig`

## Review Rules

- treat this lane as a bounded driver-starter plus review-packet lane even after the register-device request summary lands
- keep `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-closure-note.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, `Documentation/zigux/phase11-gpio-wdt-survey.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/README.md`, `zigux/tests/phase11_gpio_wdt_manifest.json`, `zigux/tests/phase11_gpio_wdt_survey.zig`, `zigux/tests/phase11_build.zig`, and `zigux/Makefile` aligned so this matrix does not drift away from the shipped shared Phase 11 replay route or the focused shared header-boundary packet
- keep `zigux/tests/phase11_build.zig` as the shared replay path for the current starter instead of adding ad hoc Phase 11 CI steps
- do not imply `zigux/tests/phase11_gpio_wdt_platform_drvdata.zig` is already wired into `zigux/tests/phase11_build.zig`; today it is focused local replay evidence that sits beside the shared packet
- do not imply a removed `validate-phase11.py`, a missing `phase11_build_inventory.json` fixture, or a broader checker-script packet that is not on `master`
- do not claim live GPIO descriptor lookup, `platform_set_drvdata()` execution, `watchdog_set_drvdata()` execution, watchdog-core registration, reboot integration, or hardware-backed execution until the Zig surface and tests for those behaviors exist
- when a later teardown-parity, failure-mode, or hardware-validation handoff lands, update this matrix, the module-slice note, the survey note, and the survey manifest together so the lane keeps one truthful next step
